#pragma once
#include <iostream>
#include <opencv2/opencv.hpp>
#include <opencv2/xphoto/white_balance.hpp>
#include <string>
#include<vector>
#include <experimental/filesystem>
#include <typeinfo>
#include <map>
#include <math.h>

using namespace std;
using namespace cv;
namespace fs = experimental::filesystem;

class Division_license {
public :
	void bubble_sort(vector < map<string, Point_<int>> >& cnt, int n);

	map<string, Mat> insert2map(string path);
	void preprocessing(Mat& imgs_gray);
	Rect labeling(Mat& imgs_gray);

	vector < map<string, Point_<int> > > find_img_contour(Mat& imgs_canny);
	void draw_img_contour2(map<string, Mat>& imgs_gray);
	vector <map<string, Point_<int> > > result_img_contour(vector < map<string, Point_<int>> >& cnt);
	void write_roi_file(Mat& imgs_gray, vector < map<string, Point_ <int> > >& result_contour_list, string write_path);
};