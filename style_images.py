# -*- coding: utf-8 -*-

import numpy as np
from tensorflow.python.keras.models import Model
from tensorflow.python.keras.layers import Input
from tensorflow.python.keras import backend as K
from tensorflow.python.keras.preprocessing.image import (
 load_img, img_to_array, array_to_img)
import train_network


def load_image(image_path, image_shape=(224, 224, 3)):
    # スタイル画像の読み込み
    style_image = load_img(image_path, target_size=image_shape[:2])
    # numpy配列に変換
    np_style_image = np.expand_dims(img_to_array(style_image), axis=0)

    return np_style_image


def style_feature(input_shape=(224, 224, 3)):
    input_data = Input(shape=input_shape, name='input_style')
    # 学習ネットワークインスタンス化
    train_net = train_network.TrainNet()
    # スタイルから特徴量を抽出するモデル構築
    style_model = train_net.rebuild_vgg16(input_data, True, False)

    return style_model


# スタイル特徴量の損失関数
def style_feature_loss(y_style, style_pred):
    # 二乗誤差
    return K.sum(K.square(
        gram_matrix(style_pred) - gram_matrix(y_style)), axis=(1, 2))


# グラム行列　=> スタイルの近さを計測
def gram_matrix(X):
    # 軸の入れ替え => batch, channel, height, width
    axis_replaced_X = K.permute_dimensions(X, (0, 3, 2, 1))
    replaced_shape = K.shape(axis_replaced_X)
    # 特徴マップ（高さと幅を1つの軸に展開）の内積をとるためのshape
    dot_shape = (replaced_shape[0], replaced_shape[1],
                 replaced_shape[2]*replaced_shape[3])
    # 実際に内積を計算する行列
    dot_X = K.reshape(axis_replaced_X, dot_shape)
    # 転置行列
    dot_X_t = K.permute_dimensions(dot_X, (0, 2, 1))
    # 行列の内積
    dot = K.batch_dot(dot_X, dot_X_t)
    norm = K.prod(K.cast(replaced_shape[1:], 'float32'))
    return dot / norm
