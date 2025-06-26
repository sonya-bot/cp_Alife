import numpy as np
import vispy
from vispy.scene import SceneCanvas
from vispy.scene import visuals
from vispy.visuals.transforms import ChainTransform, MatrixTransform
import random
# ArUcoマーカーの生成にOpenCVを使用
import cv2
from cv2 import aruco

class Aruco_Swarm_Visualizer(object):
    """ArUcoマーカーを用いたSwarmVisualizerの実装"""
    MARKER_SCALE = 0.006 # マーカーサイズの定義

    def __init__(self, width=800, height=800):
        self._canvas = SceneCanvas(size=(width, height), position=(0,0), keys='interactive', title="Aruco Visualizer "+self.__class__.__name__)
        self._view = self._canvas.central_widget.add_view()
        #self._view.camera = 'arcball'
        self._view.camera = 'panzoom'
        self._view.camera.center = (0, 0, 0)
        # self._axis = visuals.XYGrid(parent=self._view.scene)
        self._axis = visuals.GridLines(parent=self._view.scene)
        self._arrows = None
        self._markers = None
        self._num_individuals = None
        self._canvas.show()
        self._marker_images = []
        self._marker_ids = []
        self._move_scale = 1.0 / self.MARKER_SCALE  # 必要に応じて倍率を調整

    def configure_markers(self, dictionary=aruco.DICT_4X4_100, aruco_pixel_size=10, base_pixel_scale=1.2, base_color = (255,255,255)):
        """ArUcoマーカーの辞書とサイズを設定する"""
        self._dict_aruco = aruco.getPredefinedDictionary(dictionary)
        self._max_marker_id = len(self._dict_aruco.bytesList) - 1 # Aruco辞書に含まれるマーカーの総数からIDの最大値を取得
        self._aruco_pixel_size = aruco_pixel_size
        self._base_pixel_size = int(self._aruco_pixel_size * base_pixel_scale)
        self._base_color = base_color
        self._agent_visuals = []

    def _create_aruco_image(self, marker_id,  base_color = None):
        """指定されたIDの「土台付き」ArUcoマーカー画像を生成する"""
        # 色が指定されていればそれを使い、なければクラスのデフォルト色を使う
        color_to_use = self._base_color if base_color is None else base_color
        # 土台画像を作成
        img_shape = (self._base_pixel_size, self._base_pixel_size,3)
        base_img = np.ones(img_shape, dtype=np.uint8)
        base_img[:] = color_to_use
        # ArUcoマーカーを生成
        marker_img = aruco.generateImageMarker(
            self._dict_aruco, 
            marker_id, 
            self._aruco_pixel_size
        )
        # グレースケールのマーカーをRGBに変換
        marker_img_rgb = cv2.cvtColor(marker_img, cv2.COLOR_GRAY2RGB)
        # 土台の中央にマーカーを貼り付け
        offset = (self._base_pixel_size - self._aruco_pixel_size) // 2
        base_img[offset:offset + self._aruco_pixel_size, offset:offset + self._aruco_pixel_size] = marker_img_rgb
        
        return base_img
    
    def set_markers(self, position, scale=MARKER_SCALE*1.2, color=(255, 0, 0)):
        """id=0のマーカーを、動かない目印としてシーンに配置する。中心座標がマーカーの中心になるよう調整。"""
        if not hasattr(self, '_dict_aruco'):
            self.configure_markers()
            
        pos_2d = position[0, :2] * self.MARKER_SCALE
        marker_id = 0
        marker_data = self._create_aruco_image(marker_id, base_color=color)
        self._marker_ids.append(marker_id)
        self._static_marker_visual = visuals.Image(marker_data, parent=self._view.scene)
        
        # マーカー画像の中心を原点に合わせるためのオフセット
        img_shape = marker_data.shape
        center_offset = np.array([img_shape[1] / 2.0, img_shape[0] / 2.0, 0])

        scale_transform = MatrixTransform()
        scale_transform.scale((scale, scale, 1.0))

        # 画像の中心を原点に移動
        center_transform = MatrixTransform()
        center_transform.translate(-center_offset)

        # 指定位置に移動
        translate_transform = MatrixTransform()
        translate_transform.translate((pos_2d[0], pos_2d[1], 0))  * self.MARKER_SCALE

        # 順番: スケール→中心補正→平行移動
        transform = ChainTransform([scale_transform, center_transform, translate_transform])
        self._static_marker_visual.transform = transform
        self._canvas.update()
        vispy.app.process_events()

    def __bool__(self):
        return not self._canvas._closed

    def generate_markers(self,num_individuals):
        """ArUcoマーカーのテクスチャを生成する"""
        self._num_individuals = num_individuals
        self._agent_visuals = []
        marker_ids = random.sample(range(1, self._max_marker_id + 1), self._num_individuals)
        # 【追加】動的エージェントのIDをリストに記録
        self._marker_ids.extend(marker_ids)
        
        for i in range(self._num_individuals):
            marker_data = self._create_aruco_image(marker_ids[i])
            img_visual = visuals.Image(marker_data, parent=self._view.scene)
            self._agent_visuals.append(img_visual)
        print(self._marker_ids)


    def update(self, position, direction):
        """エージェントの位置と向きを更新する"""
        assert position.ndim == 2 and position.shape[1] in (2,3)
        assert direction.ndim == 2 and direction.shape[1] in (2,3)
        assert position.shape[0] == direction.shape[0]

        # 遅延初期化: 初めてupdateが呼ばれたときに動的マーカーを生成
        if self._num_individuals is None:
            if not hasattr(self, '_dict_aruco'):
                self.configure_markers()
            self.generate_markers(position.shape[0])
        
        # 各ArUcoマーカーの位置と向きを更新
        for i in range(self._num_individuals):
            pos = position[i, :2]  * (1.0 / self.MARKER_SCALE)
            directions = direction[i, :2]

            angle_rad = np.arctan2(directions[1], directions[0])
            angle_deg = np.degrees(angle_rad)

            scale = self.MARKER_SCALE
            
            # Transformの作成を複数行に分割して堅牢化
            scale_transform = MatrixTransform()
            scale_transform.scale((scale, scale, 1.0))

            rotate_transform = MatrixTransform()
            rotate_transform.rotate(angle_deg, (0, 0, 1))

            translate_transform = MatrixTransform()
            translate_transform.translate((pos[0], pos[1], 0))
            
            # 順番が重要: スケール -> 回転 -> 移動
            transform = ChainTransform([scale_transform, rotate_transform, translate_transform])
            self._agent_visuals[i].transform = transform
            
            self._agent_visuals[i].transform = transform

        self._canvas.update()
        vispy.app.process_events()


if __name__ == '__main__':
    # 注意: N=1000ではArUcoマーカーの描画が非常に遅くなる可能性があります。
    #      まずはN=100程度で試すことを強く推奨します。
    N = 10
    v = Aruco_Swarm_Visualizer() # 元のコード通り、クラスをインスタンス化
    pos = np.random.normal(size=(N, 2), scale=0.2)
    vel = np.random.normal(size=(N, 2), scale=0.2) * 0.001
    
    # set_markersも元のコード通り動作します
    # v.set_markers(np.array([[0,0,0]]))
    
    while v:
        vel -= pos * 0.00001
        pos +=  vel
        
        # updateを呼び出すと、ArUcoマーカーが更新されます
        v.update(pos, vel)