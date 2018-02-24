#include <iostream>  
#include <opencv2/core/core.hpp>  
#include <opencv2/highgui/highgui.hpp>
#include <opencv2/opencv.hpp>


using namespace cv;

int main() {
	// 读入一张图片（游戏原画）    
	Mat img = imread("pic.jpg");
	Mat gimg;
	cvtColor(img, gimg, CV_BGR2GRAY);
	imwrite("Gray_Image.jpg", gimg);
	// 创建一个名为 "游戏原画"窗口  
	Mat result;
	Canny(img, result, 15, 45);
	imwrite("Res.jpg", result);
	return 0;

}