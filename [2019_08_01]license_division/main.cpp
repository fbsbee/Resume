//#include <iostream>
//#include <opencv2/opencv.hpp>
//#include <opencv2/xphoto/white_balance.hpp>
//#include <string>
////#include<Windows.h>
//#include<vector>
////#include <boost/filesystem.hpp>
//#include <experimental/filesystem>
//#include <typeinfo>
//#include <map>
//#include <math.h>
#include "Division_license.h"
//#define PI  3.14159265358979323846
//#define PI  3.141592653
//
//using namespace std;
//using namespace cv;
//namespace fs = experimental::filesystem;
//
//
//void bubble_sort(vector < map<string, Point_<int>> >& cnt, int n) {
//	int i, j;
//	map<string, Point_<int>> temp;
//	// 작은값 E
//	//const int E = 40;
//
//	/*const double WIDTH_DIFF = 0.7;
//	const double MAX_AREA_DIFF = 1.3;
//	const double MIN_AREA_DIFF = 0.7;*/
//
//
//	for (i = n - 1; i > 0; i--) {
//		// 0 ~ (i-1)까지 반복
//		for (j = 0; j < i; j++) {
//			//double area_ratio = ((cnt[j]["br"] - cnt[j]["tl"]).x * (cnt[j]["br"] - cnt[j]["tl"]).y) / ((cnt[j + 1]["br"] - cnt[j + 1]["tl"]).x * (cnt[j + 1]["br"] - cnt[j + 1]["tl"]).y);
//			// j번째와 j+1번째의 요소가 크기 순이 아니면 교환
//			if (
//				//한 변의 길이와 다음 사각형의 좌상단 꼭지점과의 거리 비교 (일정한 사각형끼리 묶음)
//				//cnt[j]["br"].x - cnt[j]["tl"].x > cnt[j+1]["tl"].x - cnt[j]["br"].x
//				// x, y좌표 위치
//				//&&
//				cnt[j]["tl"].x > cnt[j + 1]["tl"].x
//				// 영역크기 오름차순으로
//				/*&&
//				(
//					area_ratio <= MAX_AREA_DIFF
//					&&
//					area_ratio >= MIN_AREA_DIFF
//				)*/
//				//&& cnt[j]["cxy"].y > cnt[j+1]["cxy"].y
//				)
//			{
//				temp = cnt[j];
//				cnt[j] = cnt[j + 1];
//				cnt[j + 1] = temp;
//			}
//
//		}
//
//	}
//
//}
//
//static map<string, Mat> insert2map(string path) {
//	map<string, Mat> imgs_color;
//
//	for (auto&& x : fs::recursive_directory_iterator(path)) {
//		//cout << x.path().extension() << endl;
//		if (x.path().extension() == ".jpg" || x.path().extension() == ".JPG") {
//			/*cout << x.path().generic_string() << endl;
//			cout << x.path().stem().generic_string() << endl;*/
//			imgs_color.insert(pair<string, Mat>(x.path().stem().generic_string(), imread(x.path().generic_string(), IMREAD_COLOR)));
//		}
//		//x.path().extension() == ".jpg" || x.path().extension() == ".JPG" ? cout << x.path().generic_string << endl : cout << endl;
//	}
//	cout << "input done" << endl;
//	return imgs_color;
//}
//
//void convert2gray_test(Mat& imgs_gray) {
//	if (imgs_gray.size().width >= 2000) {
//		resize(imgs_gray, imgs_gray, Size(imgs_gray.size() / 2), 0, 0, INTER_AREA);
//	}
//	cvtColor(imgs_gray, imgs_gray, COLOR_RGB2GRAY);
//	GaussianBlur(imgs_gray, imgs_gray, Size(5, 5), 0);
//	Canny(imgs_gray, imgs_gray, 100, 150);
//
//	cout << "cvt2gray, gaussian blur, canny, resize done" << endl;
//}
//
//void convert2gray(map<string, Mat>& imgs_gray) {
//	map<string, Mat>::iterator iter;
//	for (iter = imgs_gray.begin(); iter != imgs_gray.end(); iter++) {
//		//가로 세로 거리 고정. 
//		if (imgs_gray[iter->first].size().width >= 2000) {
//			resize(imgs_gray[iter->first], imgs_gray[iter->first], Size(imgs_gray[iter->first].size() / 2), 0, 0, INTER_AREA);
//		}
//		cvtColor(imgs_gray[iter->first], imgs_gray[iter->first], COLOR_RGB2GRAY);
//		GaussianBlur(imgs_gray[iter->first], imgs_gray[iter->first], Size(5, 5), 0);
//		Canny(imgs_gray[iter->first], imgs_gray[iter->first], 100, 150);
//	}
//	cout << "cvt2gray, gaussian blur, canny, resize done" << endl;
//}
//
//// 차라리 이미지 하나하나 해결하는 걸로 하고 메인 함수에서 for문 돌리는게 훨씬 나을것 같다.
//vector < map<string, Point_<int> > > find_img_contour(Mat& imgs_canny) {
//	const int MIN_AREA = 280;
//	const int MIN_WIDTH = 4;
//	const int MIN_HEIGHT = 7;
//	const double MIN_RATIO = 0.35;
//	const double MAX_RATIO = 0.85;
//
//	vector<vector<Point>> contours;
//	vector<Vec4i> hierarchy;
//
//	//map <string, Point_<int>> cnt;
//	//vector < map<string, Point_<int>> > cnt;
//
//	Scalar color = (255, 0, 0);
//	// 컨투어 찾은 후, 새로 그릴 Mat 클래스 생성
//	findContours(imgs_canny, contours, hierarchy, RETR_LIST, CHAIN_APPROX_SIMPLE);
//
//	vector <Rect> boundRect(contours.size());
//	vector<vector<Point>> approx(contours.size());
//	//Mat drawing = Mat::zeros(imgs_canny.size(), CV_8UC3);
//	double epsilon;
//	//cout << "124 line" << endl;
//	// 둘레의 길이에서 0.1을 곱함, approxPolyDP 이용.
//	for (int i = 0; i < contours.size(); i++) {
//		epsilon = 0.1 * arcLength(contours[i], true);
//		approxPolyDP(contours[i], approx[i], epsilon, true);
//		boundRect[i] = boundingRect(approx[i]);
//	}
//	//cout << "131 line" << endl;
//	vector < map<string, Point_<int> > > cnt;
//	double ratio;
//	double area;
//	// 영역 크기, 가로, 세로 길이, 길이 비율을 이용하여 사각형 걸러내기
//	for (int i = 0; i < contours.size(); i++) {
//		area = (double)boundRect[i].height * boundRect[i].width;
//		ratio = (double)boundRect[i].width / boundRect[i].height;
//
//		if (area > MIN_AREA
//			&& boundRect[i].height > MIN_HEIGHT
//			&& boundRect[i].width > MIN_WIDTH
//			&& MIN_RATIO < ratio
//			&& ratio < MAX_RATIO
//			)
//		{
//			//rectangle(drawing, boundRect[i].tl(), boundRect[i].br(), color, 1, LINE_8, 0);
//			map<string, Point_<int> > tocnt;
//			tocnt.insert(pair<string, Point_<int>>("tl", boundRect[i].tl()));
//			tocnt.insert(pair<string, Point_<int>>("br", boundRect[i].br()));
//			tocnt.insert(pair<string, Point_<int>>("cxy", (boundRect[i].tl() + (boundRect[i].br() - boundRect[i].tl()) / 2)));
//			cnt.push_back(tocnt);
//		}
//
//	}
//	// 중심점의 x 좌표 기준으로 정렬
//	bubble_sort(cnt, (int)cnt.size());
//	return cnt;
//
//}
//
//void draw_img_contour2(map<string, Mat>& imgs_gray) {
//	double epsilon;
//	double ratio;
//	double area;
//	const int MIN_AREA = 280;
//	const int MIN_WIDTH = 4;
//	const int MIN_HEIGHT = 7;
//	const double MIN_RATIO = 0.35;
//	const double MAX_RATIO = 0.85;
//
//	map <string, Mat>::iterator iter;
//	vector<vector<Point>> contours;
//	vector<Vec4i> hierarchy;
//
//	Mat drawing;
//
//	vector <Rect> boundRect(contours.size());
//	vector<vector<Point>> approx(contours.size());
//
//	//map <string, Point_<int>> cnt;
//	//vector < map<string, Point_<int>> > cnt;
//
//	Scalar color = (255, 0, 0);
//
//	// 이미지 블러 처리, 캐니 엣지 검출 후 contour 찾은 후 그림.
//	for (iter = imgs_gray.begin(); iter != imgs_gray.end(); iter++) {
//		// 가우시안 블러 적용, 캐니 엣지 적용, 컨투어 찾기
//		GaussianBlur(imgs_gray[iter->first], imgs_gray[iter->first], Size(5, 5), 0);
//		Canny(imgs_gray[iter->first], imgs_gray[iter->first], 100, 150);
//		findContours(imgs_gray[iter->first], contours, hierarchy, RETR_LIST, CHAIN_APPROX_SIMPLE);
//
//		// 새로 그릴 Mat 클래스 생성
//		drawing = Mat::zeros(imgs_gray[iter->first].size(), CV_8UC3);
//
//		// 둘레의 길이에서 0.1을 곱함, approxPolyDP 이용.
//		for (int i = 0; i < contours.size(); i++) {
//			epsilon = 0.1 * arcLength(contours[i], true);
//			approxPolyDP(contours[i], approx[i], epsilon, true);
//			boundRect[i] = boundingRect(approx[i]);
//		}
//
//		// 새로운 주소를 할당하는게 좋을지 vector값 clear해서 사용하는것이 좋을지 모르겠음 새로 초기화 하면 기존 메모리에 저장되어있던 데이터는 날아가는건가?
//		vector < map<string, Point_<int>> > cnt;
//		// 영역 크기, 가로, 세로 길이, 길이 비율을 이용하여 사각형 걸러내기
//		for (int i = 0; i < contours.size(); i++) {
//			area = (double)boundRect[i].height * boundRect[i].width;
//			ratio = (double)boundRect[i].width / boundRect[i].height;
//
//			if (area > MIN_AREA
//				&& boundRect[i].height > MIN_HEIGHT
//				&& boundRect[i].width > MIN_WIDTH
//				&& MIN_RATIO < ratio
//				&& ratio < MAX_RATIO
//				)
//			{
//				//rectangle(drawing, boundRect[i].tl(), boundRect[i].br(), color, 1, LINE_8, 0);
//				map<string, Point_<int> > tocnt;
//				tocnt.insert(pair<string, Point_<int>>("tl", boundRect[i].tl()));
//				tocnt.insert(pair<string, Point_<int>>("br", boundRect[i].br()));
//				tocnt.insert(pair<string, Point_<int>>("cxy", (boundRect[i].tl() + (boundRect[i].br() - boundRect[i].tl()) / 2)));
//				cnt.push_back(tocnt);
//			}
//
//		}
//		// 정렬
//		bubble_sort(cnt, (int)cnt.size());
//
//	}
//
//
//}
//
//vector <map<string, Point_<int> > > result_img_contour(vector < map<string, Point_<int>> >& cnt) {
//	const double PI = 3.14159265358979323846;
//
//	// 비율로 해야한다... 각도 크기, 가로길이 비율, 영역 비율
//	const int DEGREE = 30;
//	const double WIDTH_DIFF = 7.0;
//	const double MIN_AREA_DIFF = 0.6;
//	const double MAX_AREA_DIFF = 1.3;
//	const int LIST_LEN = 3;
//	const int MAX_AREA = 20000;
//	const double MIN_COORDINATE_DIFF_Y = 0.8;
//	const double MAX_COORDINATE_DIFF_Y = 1.3;
//
//	Scalar color = (255, 0, 0);
//
//	vector <map<string, Point_<int> > > before_result;
//	map<string, Point_<int> > tocnt;
//
//	for (int i = 0; i < (int)cnt.size(); i++) {
//		int rect_width = cnt[i]["br"].x - cnt[i]["tl"].x;
//
//		//rectangle(drawing, cnt[i]["tl"], cnt[i]["br"], color, 1, LINE_8, 0);
//		// j가 i 부터 시작하면 그 전 좌표,(배열)에 있는 데이터랑은 비교 안함.
//		for (int j = i; j < (int)cnt.size(); j++) {
//			if (cnt[i]["cxy"].x == cnt[j]["cxy"].x) {
//				continue;
//			}
//			//((cnt[i]["br"] - cnt[i]["tl"]).x * (cnt[i]["br"] - cnt[i]["tl"]).y) / ((cnt[j]["br"] - cnt[j]["tl"]).x * (cnt[j]["br"] - cnt[j]["tl"]).y)
//			//else if 를 if로바꾸고 그 위에 변수 적기.
//			else if (
//				// 영역 비율 비교
//				((cnt[i]["br"] - cnt[i]["tl"]).x * (cnt[i]["br"] - cnt[i]["tl"]).y) / ((cnt[j]["br"] - cnt[j]["tl"]).x * (cnt[j]["br"] - cnt[j]["tl"]).y) > MIN_AREA_DIFF
//				&&
//				((cnt[i]["br"] - cnt[i]["tl"]).x * (cnt[i]["br"] - cnt[i]["tl"]).y) / ((cnt[j]["br"] - cnt[j]["tl"]).x * (cnt[j]["br"] - cnt[j]["tl"]).y) < MAX_AREA_DIFF
//				&&
//				((cnt[j]["br"] - cnt[j]["tl"]).x * (cnt[j]["br"] - cnt[j]["tl"]).y) < MAX_AREA
//				// 각도 범위 비교
//				&&
//				atan((cnt[i]["cxy"].y - cnt[j]["cxy"].y) / (cnt[j]["cxy"].x - cnt[i]["cxy"].x)) * 180 / PI < DEGREE
//				&&
//				atan((cnt[i]["cxy"].y - cnt[j]["cxy"].y) / (cnt[j]["cxy"].x - cnt[i]["cxy"].x)) * 180 / PI > -DEGREE
//				// i번째 사각형과 j번째의 사각형의 거리비율 비교 (각 도형의 중심점 거리/ i번째 사각형의 가로 길이로 비교)
//				&&
//				(cnt[j]["cxy"].x - cnt[i]["cxy"].x) / rect_width < WIDTH_DIFF
//				&&
//				(cnt[i]["cxy"].y / cnt[j]["cxy"].y) > MIN_COORDINATE_DIFF_Y
//				&&
//				(cnt[i]["cxy"].y / cnt[j]["cxy"].y) < MAX_COORDINATE_DIFF_Y
//				)
//			{
//				/*rectangle(drawing, cnt[i]["tl"], cnt[i]["br"], Scalar(0, 255, 0), 1, LINE_8, 0);
//				rectangle(drawing, cnt[j]["tl"], cnt[j]["br"], Scalar(0,255,0), 1, LINE_8, 0);
//				cout << "거리 : " << (cnt[i]["cxy"].x - cnt[j]["cxy"].x) / rect_width << endl;
//				cout << "tl : " << cnt[j]["tl"] << endl << "br : " << cnt[j]["br"] << endl;
//				cout << j << "번쨰 영역 크기: " << ((cnt[j]["br"] - cnt[j]["tl"]).x* (cnt[j]["br"] - cnt[j]["tl"]).y) << endl;*/
//
//
//				tocnt.insert(pair<string, Point_<int>>("tl", cnt[j]["tl"]));
//				tocnt.insert(pair<string, Point_<int>>("br", cnt[j]["br"]));
//				before_result.push_back(tocnt);
//				tocnt.clear();
//				//before_result.push_back({ cnt[j]["tl"], cnt[j]["br"] });
//			}
//
//		}
//
//		if (before_result.size() < LIST_LEN) {
//			before_result.clear();
//			continue;
//		}
//		else {
//			tocnt.insert(pair<string, Point_<int>>("tl", cnt[i]["tl"]));
//			tocnt.insert(pair<string, Point_<int>>("br", cnt[i]["br"]));
//			before_result.insert(before_result.begin(), tocnt);
//			/*for (auto a : before_result) {
//				rectangle(drawing, a["tl"], a["br"], Scalar(0, 0, 255), 1, LINE_8, 0);
//			}*/
//
//			tocnt.clear();
//			break;
//		}
//
//
//	}
//	return before_result;
//}
//
//// 이미지에 사각형 그리는 함수를 따로 빼려 했지만 되려 손해보는 느낌이라
//// 전처리함과 동시에 컨투어 그림.
//
////void drawSquares(Mat& image, const vector<vector<Point> >& squares)
////{
////	Scalar color = Scalar(255, 0, 0);
////	for (size_t i = 0; i < squares.size(); i++)
////	{
////		const Point* p = &squares[i][0];
////		int n = (int)squares[i].size();
////		polylines(image, &p, &n, 1, true, color, 3, LINE_AA);
////	}
////}
//
////void drawSquares(Mat& img, const vector<vector<Point> >& contours, vector<Vec4i>& hierarchy) {
////	vector <Rect> boundRect;
////	vector<vector<Point>> approx;
////	double epsilon;
////
////	for (size_t i = 0; i < contours.size(); i++) {
////		epsilon = 0.1 * arcLength(contours[i], true);
////		approxPolyDP(contours[i], approx[i], epsilon, true);
////		boundRect[i] = boundingRect(approx[i]);
////	}
////
////	double ratio;
////	Scalar color = (255, 0, 0);
////	Mat drawing = Mat::zeros(img.size(), CV_8UC3);
////
////	for (int i = 0; i < contours.size(); i++) {
////		ratio = (double)boundRect[i].height / boundRect[i].width;
////		drawControus(drawing, contours, i, color, 1, 8, hierarchy, 0,)
////		drawContours(drawing, contours, (int)i, color, 2, LINE_8, hierarchy, 0);
////	}
////}
//
//void write_roi_file(Mat& imgs_gray, vector < map<string, Point_ <int> > >& result_contour_list, string write_path) {
//	vector <Rect> roi;
//	Point_ <int> start_point;
//	Point_ <int> end_point;
//
//	for (auto a : result_contour_list) {
//		if (a.size() == 0) {
//			continue;
//		}
//		else if (a.size() <= 4) {
//			//좌측과 위는 2/3 정도 더 넓게. 우측과 아래는 한 변의 길이만큼만.
//			//start_point = Point_ <int>((a[0]["tl"].x - (int)((a[a.size() - 1]["br"].x - a[0]["tl"].x) * 2 / 3)), (a[0]["tl"].y - (int)(a[a.size() - 1]["br"].y - a[0]["tl"].y) * 2 / 3));
//			//end_point = Point_ <int>((a[a.size() - 1]["br"].x * 2 - a[0]["tl"].x), (a[a.size() - 1]["br"].y * 2 - a[0]["tl"].y));
//			start_point = a[0]["tl"];
//			end_point = a[a.size() - 1]["br"];
//		}
//		else {
//			start_point = a[0]["tl"];
//			end_point = a[a.size() - 1]["br"];
//
//		}
//
//		roi.push_back(Rect(start_point, end_point));
//	}
//	int x = 0;
//	cout << roi.size() << endl;
//
//	map<string, Mat>::iterator iter;
//	for (iter = imgs_gray.begin(); iter != imgs_gray.end(); iter++) {
//		cout << "x : " << x << endl;
//		cout << "tl : " << roi[x].tl() << endl << "br : " << roi[x].br() << endl;
//		imwrite(write_path + iter->first + ".jpg", imgs_gray[iter->first](roi[x]));
//		x++;
//	}
//}

// vector 말고 list에다가 이미지 값 넣으면 됨. 

int main() {
	Division_license divi;
	string img_path = "C:\\Users\\Cju\\Desktop\\[2019_08_01]before_division_license";
	string write_path = "C:\\Users\\Cju\\Desktop\\[2019_08_01]after_division_license\\";
	// imgs_color는 하나만 읽고. main에 파일 열고 닫고.
	// 이미지값 넣기
	//map<string, Mat> imgs_color = divi.insert2map(img_path);
	Mat img, img_binary;
	for (auto&& x : fs::recursive_directory_iterator(img_path)) {
		if (x.path().extension() == ".jpg" || x.path().extension() == ".JPG") {
			/*cout << x.path().generic_string() << endl;
			cout << x.path().stem().generic_string() << endl;*/
			//preprocessing 을 한 후 넣는게 . main에서 열면 됨
			img = imread(x.path().generic_string(), IMREAD_COLOR);
			img.copyTo(img_binary);

			divi.preprocessing(img_binary);

			imwrite(write_path + x.path().stem().generic_string() + ".jpg", img_binary(divi.labeling(img_binary)));

			/*imgs_color.insert(pair<string, Mat>(x.path().stem().generic_string(), imread(x.path().generic_string(), IMREAD_COLOR)));
			divi.preprocessing(imgs_gray[iter->first]);*/
		}
		cout << x.path().stem().generic_string() << ".jpg write done " << endl;
		//x.path().extension() == ".jpg" || x.path().extension() == ".JPG" ? cout << x.path().generic_string << endl : cout << endl;
	}
	cout << "done" << endl;
	//map<string, Mat> imgs_gray(imgs_color);
	//cout << &imgs_color["1"].data << endl;
	//cout << &imgs_gray["1"].data << endl;
	//cout << "input done" << endl;
	//
	//// 전처리 과정
	//map<string, Mat>::iterator iter;
	//for (iter = imgs_gray.begin(); iter != imgs_gray.end(); iter++) {
	//	divi.preprocessing(imgs_gray[iter->first]);
	//}
	//cout << "cvt2hsv, gaussian blur, white balance, " << endl;
	//
	////라벨링 , roi 반환
	////resize 후 저장할 수도 있겠다. 
	////resize(imgs_gray[iter->first](divi.labeling(imgs_gray[iter->first])), imgs_gray[iter->first], Size(imgs_gray[iter->first].size() / 2), 0, 0, INTER_AREA);
	//for (iter = imgs_gray.begin(); iter != imgs_gray.end(); iter++) {
	//	imwrite(write_path + iter->first + ".jpg", imgs_gray[iter->first](divi.labeling(imgs_gray[iter->first])));
	//}
	//==============================================
	/*cv::imshow("color", imgs_color["39"]);
	cv::imshow("gray", imgs_gray["39"]);
	cv::waitKey(0);
	cv::imshow("color", imgs_color["139"]);
	cv::imshow("gray", imgs_gray["139"]);
	cv::waitKey(0);*/
	// contour 하는 과정
	////vector < map<string, Point_ <int> > > contour_list;
	//vector < vector < map<string, Point_ <int> > > > result_contour_list;

	//for (iter = imgs_gray.begin(); iter != imgs_gray.end(); iter++) {
	//	//contour_list = find_img_contour(imgs_gray[iter->first]);
	//	//result_contour_list.push_back(result_img_contour(contour_list));
	//	result_contour_list.push_back((divi.find_img_contour(imgs_gray[iter->first])));
	//	//divi.write_roi_file(imgs_gray[iter->first], divi.find_img_contour(imgs_gray[iter->first]), write_path);
	//}
	//cout << "380 line" << endl;

	//// 어파인 변환을 roi 저장전에 하면 될듯

	//// roi 저장
	//vector <Rect> roi;
	//Point_ <int> start_point;
	//Point_ <int> end_point;

	//for (auto a : result_contour_list) {
	//	cout << "a.size() : " << a.size() << endl;
	//	if (a.size() == 0) {
	//		continue;
	//	}
	//	else if (a.size() <= 4) {
	//		//좌측과 위는 2/3 정도 더 넓게. 우측과 아래는 한 변의 길이만큼만.
	//		start_point = Point_ <int>((a[0]["tl"].x - (int)((a[a.size() - 1]["br"].x - a[0]["tl"].x) * 2 / 3)), (a[0]["tl"].y - (int)(a[a.size() - 1]["br"].y - a[0]["tl"].y) * 2 / 3));
	//		end_point = Point_ <int>((a[a.size() - 1]["br"].x * 2 - a[0]["tl"].x), (a[a.size() - 1]["br"].y * 2 - a[0]["tl"].y));
	//		//start_point = a[0]["tl"];
	//		//end_point = a[a.size() - 1]["br"];
	//	}
	//	else {
	//		start_point = a[0]["tl"];
	//		end_point = a[a.size() - 1]["br"];

	//	}

	//	roi.push_back(Rect(start_point, end_point));
	//}
	//int x = 0;
	//cout << "here" << endl;
	//cout << roi.size() << endl;

	//for (iter = imgs_gray.begin(); iter != imgs_gray.end(); iter++) {
	//	cout << "x : " << x << endl;
	//	cout << "tl : " << roi[x].tl() << endl << "br : " << roi[x].br() << endl;
	//	imwrite(write_path + iter->first + ".jpg", imgs_gray[iter->first](roi[x]));
	//	x++;
	//}


	//cv::imshow("color", imgs_color["0"]);
	//cv::imshow("gray", imgs_gray["0"]);
	//cv::waitKey(0);
	//Mat drawing = Mat::zeros(imgs_gray["3"].size(), CV_8UC3);
	//drawSquares(imgs_gray["3"], squares);
	//drawContours(drawing, approx, 0, color, 2);

	//cv::imshow("contours", drawing);
	//imshow("contours", drawing);

	//==============================================

	//vector<vector<Point>> contours;
	//vector<Vec4i> hierarchy;

	//findContours(imgs_gray["3"], contours, hierarchy, RETR_LIST, CHAIN_APPROX_SIMPLE);
	//
	//Mat drawing = Mat::zeros(imgs_gray["3"].size(), CV_8UC3);
	//Scalar color = Scalar(255, 0, 0);

	////vector <Point> approx;

	//double epsilon;

	//////허프 변환
	////vector<Vec4i> lines;
	////HoughLinesP(imgs_gray["3"], lines, 1, CV_PI / 180, 100, 20, 1);

	////for (int i = 0; i < lines.size(); i++)
	////{
	////	Vec4i L = lines[i];
	////	line(drawing, Point(L[0], L[1]), Point(L[2], L[3]),
	////		color, 1, LINE_AA);
	////}
	//vector <Rect> boundRect(contours.size());
	//vector<vector<Point>> approx(contours.size());


	//for (size_t i = 0; i < contours.size(); i++) {
	//	epsilon = (double) 0.1 * arcLength(contours[i], true);
	//	approxPolyDP(contours[i], approx[i], epsilon, true);
	//	
	//	boundRect[(int)i] = boundingRect(contours[i]);
	//	
	//}
	////너무 조그마한 것은 어차피 검출 안되겠고 적당한 크기이상으로. 대신 비율을 맞춰서.
	//double ratio;
	//double area;
	//const int MIN_AREA = 280;
	//const int MIN_WIDTH = 4;
	//const int MIN_HEIGHT = 7;
	//const double MIN_RATIO = 0.35;
	//const double MAX_RATIO = 0.85;

	////map <string, Point_<int>> cnt
	//
	//vector < map<string, Point_<int>> > cnt;

	//for (int i = 0; i < contours.size(); i++) {
	//	area = (double)boundRect[i].height * boundRect[i].width;
	//	ratio = (double)boundRect[i].width / boundRect[i].height;
	//	if (area > MIN_AREA 
	//		&& boundRect[i].height > MIN_HEIGHT
	//		&& boundRect[i].width > MIN_WIDTH
	//		&& MIN_RATIO < ratio 
	//		&& ratio < MAX_RATIO
	//		) 
	//	{
	//		//사각형 그려넣는 함수
	//		//rectangle(drawing, boundRect[i].tl(), boundRect[i].br(), color, 1, LINE_8, 0);

	//		//cnt.push_back(tocnt.insert(make_pair("ti", boundRect[i].tl())));

	//		// 배열안에 map 넣기
	//		map<string, Point_<int> > tocnt;
	//		tocnt.insert(pair<string, Point_<int>>("tl", boundRect[i].tl()));
	//		tocnt.insert(pair<string, Point_<int>>("br", boundRect[i].br()));
	//		tocnt.insert(pair<string, Point_<int>>("cxy", (boundRect[i].tl() + (boundRect[i].br() - boundRect[i].tl()) / 2)));
	//		cnt.push_back(tocnt);

	//		/*cnt["tl"] = boundRect[i].tl();
	//		cnt["br"] = boundRect[i].br();
	//		cnt["cxy"] = (boundRect[i].tl() + (boundRect[i].br() - boundRect[i].tl()) / 2);*/
	//	}

	//}
	//
	////버블 정렬 해야 함
	//cout << "cnt size() : " << cnt.size() <<endl;

	//bubble_sort(cnt, (int)cnt.size());

	///*for (auto a : cnt) {
	//	cout << "tl : " << a["tl"] << endl << "br : " << a["br"] << endl;

	//}*/

	////16 시작 , /2 +5 끝
	//const double PI = 3.14159265358979323846;

	//// 비율로 해야한다... 각도 크기, 가로길이 비율, 영역 비율
	//const int DEGREE = 20;
	//const double WIDTH_DIFF = 7.0;
	//const double MIN_AREA_DIFF = 0.6;
	//const double MAX_AREA_DIFF = 1.3;
	//const int LIST_LEN = 3;
	//const int MAX_AREA = 20000;
	//const double MIN_COORDINATE_DIFF_Y = 0.8;
	//const double MAX_COORDINATE_DIFF_Y = 1.3;

	//vector <map<string, Point_<int> > > before_result;
	//map<string, Point_<int> > tocnt;

	//for (int i = 0; i < (int)cnt.size(); i++) {
	//	int rect_width = cnt[i]["br"].x - cnt[i]["tl"].x;

	//	rectangle(drawing, cnt[i]["tl"], cnt[i]["br"], color, 1, LINE_8, 0);
	//	// j가 i 부터 시작하면 그 전 좌표,(배열)에 있는 데이터랑은 비교 안함.
	//	for (int j = i; j < (int)cnt.size(); j++) {
	//		if (cnt[i]["cxy"].x == cnt[j]["cxy"].x) {
	//			continue;
	//		}
	//		else if (
	//			// 영역 비율 비교
	//			((cnt[i]["br"] - cnt[i]["tl"]).x * (cnt[i]["br"] - cnt[i]["tl"]).y) / ((cnt[j]["br"] - cnt[j]["tl"]).x * (cnt[j]["br"] - cnt[j]["tl"]).y) > MIN_AREA_DIFF
	//			&&
	//			((cnt[i]["br"] - cnt[i]["tl"]).x * (cnt[i]["br"] - cnt[i]["tl"]).y) / ((cnt[j]["br"] - cnt[j]["tl"]).x * (cnt[j]["br"] - cnt[j]["tl"]).y) < MAX_AREA_DIFF
	//			&&
	//			((cnt[j]["br"] - cnt[j]["tl"]).x * (cnt[j]["br"] - cnt[j]["tl"]).y) < MAX_AREA
	//			// 각도 범위 비교
	//			&&
	//			atan((cnt[i]["cxy"].y - cnt[j]["cxy"].y) / (cnt[j]["cxy"].x - cnt[i]["cxy"].x)) * 180 / PI < DEGREE
	//			&&
	//			atan((cnt[i]["cxy"].y - cnt[j]["cxy"].y) / (cnt[j]["cxy"].x - cnt[i]["cxy"].x)) * 180 / PI > -DEGREE
	//			//i번째 사각형과 j번째의 사각형의 거리비율 비교 (각 도형의 중심점 거리/ i번째 사각형의 가로 길이로 비교)
	//			&&
	//			(cnt[j]["cxy"].x - cnt[i]["cxy"].x) / rect_width < WIDTH_DIFF
	//			&&
	//			(cnt[i]["cxy"].y / cnt[j]["cxy"].y) > MIN_COORDINATE_DIFF_Y
	//			&&
	//			(cnt[i]["cxy"].y / cnt[j]["cxy"].y) < MAX_COORDINATE_DIFF_Y

	//			)
	//		{
	//			/*rectangle(drawing, cnt[i]["tl"], cnt[i]["br"], Scalar(0, 255, 0), 1, LINE_8, 0);
	//			rectangle(drawing, cnt[j]["tl"], cnt[j]["br"], Scalar(0,255,0), 1, LINE_8, 0);
	//			cout << "거리하는건데 이거 어떻게 나오지 " << (cnt[i]["cxy"].x - cnt[j]["cxy"].x) / rect_width << endl;
	//			cout << "tl : " << cnt[j]["tl"] << endl << "br : " << cnt[j]["br"] << endl;
	//			cout << j << "번쨰 영역 크기: " << ((cnt[j]["br"] - cnt[j]["tl"]).x* (cnt[j]["br"] - cnt[j]["tl"]).y) << endl;*/

	//			
	//			tocnt.insert(pair<string, Point_<int>>("tl", cnt[j]["tl"]) );
	//			tocnt.insert(pair<string, Point_<int>>("br", cnt[j]["br"]) );
	//			before_result.push_back(tocnt);
	//			tocnt.clear();
	//			//before_result.push_back({ cnt[j]["tl"], cnt[j]["br"] });
	//		}

	//	}

	//	if (before_result.size() < LIST_LEN) {
	//		before_result.clear();
	//		continue;
	//	}
	//	else {
	//		tocnt.insert(pair<string, Point_<int>>("tl", cnt[i]["tl"]));
	//		tocnt.insert(pair<string, Point_<int>>("br", cnt[i]["br"]));
	//		before_result.insert(before_result.begin(), tocnt);
	//		cout << "list size : " << before_result.size() << endl;
	//		for (auto a : before_result) {
	//			rectangle(drawing, a["tl"], a["br"], Scalar(0, 0, 255), 1, LINE_8, 0);
	//		}
	//		
	//		tocnt.clear();
	//		break;
	//	}
	//	
	//	

	//}
	//cv::imshow("color", imgs_color["242"]);
	//cv::imshow("gray", imgs_gray["3"]);
	//cv::imshow("contours", drawing);
	//cv::waitKey(0);

	////for (int i = 0; i < (int)cnt.size() - 1; i++) {

	////	rectangle(drawing, cnt[i]["tl"], cnt[i]["br"], Scalar(0, 255, 0), 1, LINE_8, 0);
	////	cout << "tl : " << cnt[i]["tl"] << endl << "br : " << cnt[i]["br"] << endl;
	////	cout << i << "번쨰 영역 크기: " << ((cnt[i]["br"] - cnt[i]["tl"]).x * (cnt[i]["br"] - cnt[i]["tl"]).y) << endl;

	////	// 사각형의 가로 길이와, 이번 사각형과 다음 사각형의 중심점으로부터의 거리가 비슷
	////	// 각도랑 방금 사용했던 중심점 거리 사용하되, 사각형 안에 사각형이 있을 수 있으니 거리가 진짜 작으면 continue 이건 위에서 영역 처리 해서 안해도 될듯. 4개이상이어야 함.

	////	int rect_width = cnt[i]["br"].x - cnt[i]["tl"].x;
	////	
	////	//cout << "tl : " << cnt[i]["tl"] << endl << "br : " << cnt[i]["br"] << endl;
	////	if (cnt[i]["cxy"].x == cnt[i + 1]["cxy"].x) {
	////		continue;
	////	}
	////	else if (
	////		// 이것도 비율로 바꿔야 하는데 조금 있다가
	////		rect_width - 15 < cnt[i + 1]["cxy"].x - cnt[i]["cxy"].x && rect_width + 15 > cnt[i + 1]["cxy"].x - cnt[i]["cxy"].x
	////		// 두 중심점 사이의 각도
	////		&&
	////		atan((cnt[i]["cxy"].y - cnt[i + 1]["cxy"].y) / (cnt[i + 1]["cxy"].x - cnt[i]["cxy"].x)) * 180 / PI < DEGREE
	////		&&
	////		atan((cnt[i]["cxy"].y - cnt[i + 1]["cxy"].y) / (cnt[i + 1]["cxy"].x - cnt[i]["cxy"].x)) * 180 / PI > -DEGREE
	////		//
	////		)
	////	{
	////		rectangle(drawing, cnt[i]["tl"], cnt[i]["br"], color, 1, LINE_8, 0);
	////		//rectangle(drawing, cnt[i+1]["tl"], cnt[i+1]["br"], color, 1, LINE_8, 0);
	////		cout << "======================" << endl;
	////		cout << "tl : " << cnt[i]["tl"] << endl << "br : " << cnt[i]["br"] << endl;
	////		cout << i << "번쨰 영역 크기: " << ((cnt[i]["br"] - cnt[i]["tl"]).x * (cnt[i]["br"] - cnt[i]["tl"]).y) << endl;
	////		cout << "각도 크기 : " << atan((cnt[i]["cxy"].y - cnt[i + 1]["cxy"].y) / (cnt[i + 1]["cxy"].x - cnt[i]["cxy"].x)) * 180 / PI << endl;
	////		cout << "======================" << endl;

	////	}

	////}


	////drawSquares(imgs_gray["3"], squares);
	////drawContours(drawing, approx, 0, color, 2);

	////imshow("contours", drawing);
	return 0;
}