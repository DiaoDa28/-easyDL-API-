import json
import base64
import requests
from PIL import Image , ImageDraw 
from PySide6.QtWidgets import QApplication , QWidget , QLineEdit , QPushButton ,QFileDialog
from PySide6.QtGui import QPixmap
from Ui_untitled import Ui_Form

class MyWindow(QWidget, Ui_Form): 
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        # 初始化API值
        # 可选的请求参数
        # threshold: 默认值为建议阈值，请在 我的模型-模型效果-完整评估结果-详细评估 查看建议阈值
        self.PARAMS = {"threshold": 0.3}

        # 服务详情 中的 接口地址
        self.MODEL_API_URL = "   "  #输入你在easyDL 训练后的api URL

        # 调用 API 需要 ACCESS_TOKEN。若已有 ACCESS_TOKEN 则于下方填入该字符串
        # 否则，留空 ACCESS_TOKEN，于下方填入 该模型部署的 API_KEY 以及 SECRET_KEY，会自动申请并显示新 ACCESS_TOKEN
        self.ACCESS_TOKEN = ""
        self.API_KEY = ""       #输入你在easyDL 训练后的API_KEY
        self.SECRET_KEY = ""    #输入你在easyDL 训练后的SECRET_KEY
        #获取图片的地址
        self.pushButton_2.clicked.connect(self.file_path_play)
        self.pushButton.clicked.connect(self.seed)

    def file_path_play(self):
        self.file_path, _ = QFileDialog.getOpenFileName(window, "选择文件")
        if self.file_path:
            self.label.setPixmap(QPixmap(self.file_path))
            self.label.setScaledContents(True)

    def seed(self):
        IMAGE_FILEPATH = self.file_path
        with open(IMAGE_FILEPATH, 'rb') as f:
            base64_data = base64.b64encode(f.read())
            base64_str = base64_data.decode('UTF8')
        print("将 BASE64 编码后图片的字符串填入 PARAMS 的 'image' 字段")
        self.PARAMS["image"] = base64_str

        if not self.ACCESS_TOKEN:
            print("2. ACCESS_TOKEN 为空，调用鉴权接口获取TOKEN")
            auth_url = "https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials"               "&client_id={}&client_secret={}".format(self.API_KEY, self.SECRET_KEY)
            auth_resp = requests.get(auth_url)
            auth_resp_json = auth_resp.json()
            ACCESS_TOKEN = auth_resp_json["access_token"]
            print("新 ACCESS_TOKEN: {}".format(ACCESS_TOKEN))
        else:
            print("2. 使用已有 ACCESS_TOKEN")


        print("3. 向模型接口 'MODEL_API_URL' 发送请求")
        request_url = "{}?access_token={}".format(self.MODEL_API_URL, ACCESS_TOKEN)
        response = requests.post(url=request_url, json=self.PARAMS)
        response_json = response.json()
        self.response_str = json.dumps(response_json, indent=4, ensure_ascii=False)
        print("结果:{}".format(self.response_str))
        self.mark()

    def mark (self):
        img = Image.open(self.file_path)
        img = img.convert("RGB")

        response_dict = json.loads(self.response_str)
        
        for result in response_dict["results"]:
            location_data = result["location"]
        # 计算矩形框的四个点的坐标
            right = location_data["left"] + location_data["width"]
            bottom = location_data["top"] + location_data["height"]
        # 创建一个可在图像上绘图的对象
            draw = ImageDraw.Draw(img)
        # 画矩形框
            draw.rectangle([location_data["left"], location_data["top"], right, bottom], outline="red",width=3)
        # 保存带有框的图片
        img.save(f"{self.file_path[:-4]}_over.png")

        self.label_2.setPixmap(QPixmap(f"{self.file_path[:-4]}_over.png"))
        self.label_2.setScaledContents(True)
            

if __name__ == '__main__':
    app = QApplication([])
    window = MyWindow()
    window.show()
    app.exec()

