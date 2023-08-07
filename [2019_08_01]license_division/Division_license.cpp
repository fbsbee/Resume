#include "Division_license.h"

void Division_license::bubble_sort(vector<map<string, Point_<int>>>& cnt, int n)
{
	int i, j;
	map<string, Point_<int>> temp;
	// 작은값 E
	//const int E = 40;

	/*const double WIDTH_DIFF = 0.7;
	const double MAX_AREA_DIFF = 1.3;
	const double MIN_AREA_DIFF = 0.7;*/


	for (i = n - 1; i > 0; i--) {
		// 0 ~ (i-1)까지 반복
		for (j = 0; j < i; j++) {
			//double area_ratio = ((cnt[j]["br"] - cnt[j]["tl"]).x * (cnt[j]["br"] - cnt[j]["tl"]).y) / ((cnt[j + 1]["br"] - cnt[j + 1]["tl"]).x * (cnt[j + 1]["br"] - cnt[j + 1]["tl"]).y);
			// j번째와 j+1번째의 요소가 크기 순이 아니면 교환
			if (
				//한 변의 길이와 다음 사각형의 좌상단 꼭지점과의 거리 비교 (일정한 사각형끼리 묶음)
				//cnt[j]["br"].x - cnt[j]["tl"].x > cnt[j+1]["tl"].x - cnt[j]["br"].x
				// x, y좌표 위치
				//&&
				cnt[j]["tl"].x > cnt[j + 1]["tl"].x
				// 영역크기 오름차순으로
				/*&&
				(
					area_ratio <= MAX_AREA_DIFF
					&&
					area_ratio >= MIN_AREA_DIFF
				)*/
				//&& cnt[j]["cxy"].y > cnt[j+1]["cxy"].y
				)
			{
				temp = cnt[j];
				cnt[j] = cnt[j + 1];
				cnt[j + 1] = temp;
			}

		}
	}
}

map <string, Mat> Division_license::insert2map(string path) {
	map<string, Mat> imgs_color;

	for (auto&& x : fs::recursive_directory_iterator(path)) {
		//cout << x.path().extension() << endl;
		if (x.path().extension() == ".jpg" || x.path().extension() == ".JPG") {
			/*cout << x.path().generic_string() << endl;
			cout << x.path().stem().generic_string() << endl;*/
			//preprocessing 을 한 후 넣는게 . main에서 열면 됨
			imgs_color.insert(pair<string, Mat>(x.path().stem().generic_string(), imread(x.path().generic_string(), IMREAD_COLOR)));
		}
		//x.path().extension() == ".jpg" || x.path().extension() == ".JPG" ? cout << x.path().generic_string << endl : cout << endl;
	}
	
	return imgs_color;
}

void Division_license::preprocessing(Mat & imgs_gray) {
	//if (imgs_gray.size().width >= 2000) {
		//resize(imgs_gray, imgs_gray, Size(imgs_gray.size() / 2), 0, 0, INTER_AREA);
	//}

	// 화이트 밸런스 조절 후 가우시안 블러
	cv::Ptr<cv::xphoto::WhiteBalancer> wb = cv::xphoto::createSimpleWB();
	Size mask = Size(5, 5);
	wb->balanceWhite(imgs_gray, imgs_gray);
	GaussianBlur(imgs_gray, imgs_gray, mask, 0);
	
	cvtColor(imgs_gray, imgs_gray, COLOR_RGB2HSV);
	//이진화 후 모폴로지 
	Scalar lower_green = Scalar(32, 25, 32);
	Scalar upper_green = Scalar(68, 255, 255);
	inRange(imgs_gray, lower_green, upper_green, imgs_gray);
	//Matx<uchar, 3, 3> mask;
	//mask << 0, 1, 0,
				//1, 1, 1,
				//0, 1, 0;
	//morphologyEx(imgs_gray, imgs_gray, MORPH_OPEN, mask);
	//morphologyEx(imgs_gray, imgs_gray, MORPH_CLOSE, mask);
	// 모폴로지 연산 opening
	erode(imgs_gray, imgs_gray, getStructuringElement(MORPH_ELLIPSE, mask));
	dilate(imgs_gray, imgs_gray, getStructuringElement(MORPH_ELLIPSE, mask));
	//bitwise_not(imgs_gray, imgs_gray);
	//구멍 메우기 
	//dilate(imgs_gray, imgs_gray, getStructuringElement(MORPH_ELLIPSE, Size(5, 5)));
	//erode(imgs_gray, imgs_gray, getStructuringElement(MORPH_ELLIPSE, Size(5, 5)));
	//Canny(imgs_gray, imgs_gray, 100, 150);
	
}

Rect Division_license::labeling(Mat& imgs_gray) {
	//라벨링 
	Mat img_labels, stats, centroids;
	int numOfLables = connectedComponentsWithStats(imgs_gray, img_labels, stats, centroids, 8, CV_32S);
	
	//영역박스 그리기
	int max = -1, idx = 0;
	const int MIN_AREA = 20;
	/*const int MIN_WIDTH = 4;
	const int MIN_HEIGHT = 7;*/

	for (int j = 1; j < numOfLables; j++) {
		int area = stats.at<int>(j, CC_STAT_AREA);
		int width = stats.at<int>(j, CC_STAT_WIDTH);
		int height = stats.at<int>(j, CC_STAT_HEIGHT);
		double ratio = (double)(width) / (height);

		//cout << "area : " << area << endl << "area2 : " << area2 << endl << "===========" << endl;
		if (ratio >= 2.7 || ratio <=1.4 ) {
			continue;
		}
		if (max < area)
		{
			max = area;
			idx = j;
		}
	}
	int left = stats.at<int>(idx, CC_STAT_LEFT);
	int top = stats.at<int>(idx, CC_STAT_TOP);
	int width = stats.at<int>(idx, CC_STAT_WIDTH);
	int height = stats.at<int>(idx, CC_STAT_HEIGHT);
	//cout << left<< endl<<top << endl << width << endl << height << endl;
	//rectangle은 잠깐 테스트용인데
	//cvtColor(imgs_gray, imgs_gray, COLOR_GRAY2BGR);
	//rectangle(imgs_gray, Point(left, top), Point(left + width, top + height), Scalar(0, 0, 255), 3);

	Rect roi = Rect(Point_<int>(left, top), Point_<int>(left + width, top + height));
	return roi;
}

// 차라리 이미지 하나하나 해결하는 걸로 하고 메인 함수에서 for문 돌리는게 훨씬 나을것 같다.
vector< map<string, Point_<int> > > Division_license::find_img_contour(Mat & imgs_canny) {
	const int MIN_AREA = 280;
	const int MIN_WIDTH = 4;
	const int MIN_HEIGHT = 7;
	const double MIN_RATIO = 0.35;
	const double MAX_RATIO = 0.85;

	vector<vector<Point>> contours;
	vector<Vec4i> hierarchy;

	//map <string, Point_<int>> cnt;
	//vector < map<string, Point_<int>> > cnt;

	Scalar color = Scalar(255, 0, 0);
	// 컨투어 찾은 후, 새로 그릴 Mat 클래스 생성
	findContours(imgs_canny, contours, hierarchy, RETR_LIST, CHAIN_APPROX_SIMPLE);

	vector <Rect> boundRect(contours.size());
	vector<vector<Point>> approx(contours.size());
	//Mat drawing = Mat::zeros(imgs_canny.size(), CV_8UC3);
	double epsilon;
	//cout << "124 line" << endl;
	// 둘레의 길이에서 0.1을 곱함, approxPolyDP 이용.
	for (int i = 0; i < contours.size(); i++) {
		epsilon = 0.1 * arcLength(contours[i], true);
		approxPolyDP(contours[i], approx[i], epsilon, true);
		boundRect[i] = boundingRect(approx[i]);
	}
	//cout << "131 line" << endl;
	vector < map<string, Point_<int> > > cnt;
	double ratio;
	double area;
	// 영역 크기, 가로, 세로 길이, 길이 비율을 이용하여 사각형 걸러내기
	for (int i = 0; i < contours.size(); i++) {
		area = (double)boundRect[i].height * boundRect[i].width;
		ratio = (double)boundRect[i].width / boundRect[i].height;

		if (area > MIN_AREA
			&& boundRect[i].height > MIN_HEIGHT
			&& boundRect[i].width > MIN_WIDTH
			&& MIN_RATIO < ratio
			&& ratio < MAX_RATIO
			)
		{
			//rectangle(drawing, boundRect[i].tl(), boundRect[i].br(), color, 1, LINE_8, 0);
			map<string, Point_<int> > tocnt;
			tocnt.insert(pair<string, Point_<int>>("tl", boundRect[i].tl()));
			tocnt.insert(pair<string, Point_<int>>("br", boundRect[i].br()));
			tocnt.insert(pair<string, Point_<int>>("cxy", (boundRect[i].tl() + (boundRect[i].br() - boundRect[i].tl()) / 2)));
			cnt.push_back(tocnt);
		}

	}
	// 중심점의 x 좌표 기준으로 정렬
	bubble_sort(cnt, (int)cnt.size());
	return cnt;

}

void Division_license::draw_img_contour2(map<string, Mat> & imgs_gray) {
	double epsilon;
	double ratio;
	double area;
	const int MIN_AREA = 280;
	const int MIN_WIDTH = 4;
	const int MIN_HEIGHT = 7;
	const double MIN_RATIO = 0.35;
	const double MAX_RATIO = 0.85;

	map <string, Mat>::iterator iter;
	vector<vector<Point>> contours;
	vector<Vec4i> hierarchy;

	Mat drawing;

	vector <Rect> boundRect(contours.size());
	vector<vector<Point>> approx(contours.size());

	//map <string, Point_<int>> cnt;
	//vector < map<string, Point_<int>> > cnt;

	Scalar color = (255, 0, 0);

	// 이미지 블러 처리, 캐니 엣지 검출 후 contour 찾은 후 그림.
	for (iter = imgs_gray.begin(); iter != imgs_gray.end(); iter++) {
		// 가우시안 블러 적용, 캐니 엣지 적용, 컨투어 찾기
		GaussianBlur(imgs_gray[iter->first], imgs_gray[iter->first], Size(5, 5), 0);
		Canny(imgs_gray[iter->first], imgs_gray[iter->first], 100, 150);
		findContours(imgs_gray[iter->first], contours, hierarchy, RETR_LIST, CHAIN_APPROX_SIMPLE);

		// 새로 그릴 Mat 클래스 생성
		drawing = Mat::zeros(imgs_gray[iter->first].size(), CV_8UC3);

		// 둘레의 길이에서 0.1을 곱함, approxPolyDP 이용.
		for (int i = 0; i < contours.size(); i++) {
			epsilon = 0.1 * arcLength(contours[i], true);
			approxPolyDP(contours[i], approx[i], epsilon, true);
			boundRect[i] = boundingRect(approx[i]);
		}

		// 새로운 주소를 할당하는게 좋을지 vector값 clear해서 사용하는것이 좋을지 모르겠음 새로 초기화 하면 기존 메모리에 저장되어있던 데이터는 날아가는건가?
		vector < map<string, Point_<int>> > cnt;
		// 영역 크기, 가로, 세로 길이, 길이 비율을 이용하여 사각형 걸러내기
		for (int i = 0; i < contours.size(); i++) {
			area = (double)boundRect[i].height * boundRect[i].width;
			ratio = (double)boundRect[i].width / boundRect[i].height;

			if (area > MIN_AREA
				&& boundRect[i].height > MIN_HEIGHT
				&& boundRect[i].width > MIN_WIDTH
				&& MIN_RATIO < ratio
				&& ratio < MAX_RATIO
				)
			{
				//rectangle(drawing, boundRect[i].tl(), boundRect[i].br(), color, 1, LINE_8, 0);
				map<string, Point_<int> > tocnt;
				tocnt.insert(pair<string, Point_<int>>("tl", boundRect[i].tl()));
				tocnt.insert(pair<string, Point_<int>>("br", boundRect[i].br()));
				tocnt.insert(pair<string, Point_<int>>("cxy", (boundRect[i].tl() + (boundRect[i].br() - boundRect[i].tl()) / 2)));
				cnt.push_back(tocnt);
			}

		}
		// 정렬
		bubble_sort(cnt, (int)cnt.size());

	}


}

vector<map<string, Point_<int> > >Division_license::result_img_contour(vector < map<string, Point_<int>> > & cnt) {
	const double PI = 3.14159265358979323846;

	// 비율로 해야한다... 각도 크기, 가로길이 비율, 영역 비율
	const int DEGREE = 30;
	const double WIDTH_DIFF = 7.0;
	const double MIN_AREA_DIFF = 0.6;
	const double MAX_AREA_DIFF = 1.3;
	const int LIST_LEN = 3;
	const int MAX_AREA = 20000;
	const double MIN_COORDINATE_DIFF_Y = 0.8;
	const double MAX_COORDINATE_DIFF_Y = 1.3;

	Scalar color = (255, 0, 0);

	vector <map<string, Point_<int> > > before_result;
	map<string, Point_<int> > tocnt;

	for (int i = 0; i < (int)cnt.size(); i++) {
		int rect_width = cnt[i]["br"].x - cnt[i]["tl"].x;

		//rectangle(drawing, cnt[i]["tl"], cnt[i]["br"], color, 1, LINE_8, 0);
		// j가 i 부터 시작하면 그 전 좌표,(배열)에 있는 데이터랑은 비교 안함.
		for (int j = i; j < (int)cnt.size(); j++) {
			if (cnt[i]["cxy"].x == cnt[j]["cxy"].x) {
				continue;
			}
			//((cnt[i]["br"] - cnt[i]["tl"]).x * (cnt[i]["br"] - cnt[i]["tl"]).y) / ((cnt[j]["br"] - cnt[j]["tl"]).x * (cnt[j]["br"] - cnt[j]["tl"]).y)
			//else if 를 if로바꾸고 그 위에 변수 적기.
			else if (
				// 영역 비율 비교
				((cnt[i]["br"] - cnt[i]["tl"]).x * (cnt[i]["br"] - cnt[i]["tl"]).y) / ((cnt[j]["br"] - cnt[j]["tl"]).x * (cnt[j]["br"] - cnt[j]["tl"]).y) > MIN_AREA_DIFF
				&&
				((cnt[i]["br"] - cnt[i]["tl"]).x * (cnt[i]["br"] - cnt[i]["tl"]).y) / ((cnt[j]["br"] - cnt[j]["tl"]).x * (cnt[j]["br"] - cnt[j]["tl"]).y) < MAX_AREA_DIFF
				&&
				((cnt[j]["br"] - cnt[j]["tl"]).x * (cnt[j]["br"] - cnt[j]["tl"]).y) < MAX_AREA
				// 각도 범위 비교
				&&
				atan((cnt[i]["cxy"].y - cnt[j]["cxy"].y) / (cnt[j]["cxy"].x - cnt[i]["cxy"].x)) * 180 / PI < DEGREE
				&&
				atan((cnt[i]["cxy"].y - cnt[j]["cxy"].y) / (cnt[j]["cxy"].x - cnt[i]["cxy"].x)) * 180 / PI > -DEGREE
				// i번째 사각형과 j번째의 사각형의 거리비율 비교 (각 도형의 중심점 거리/ i번째 사각형의 가로 길이로 비교)
				&&
				(cnt[j]["cxy"].x - cnt[i]["cxy"].x) / rect_width < WIDTH_DIFF
				&&
				(cnt[i]["cxy"].y / cnt[j]["cxy"].y) > MIN_COORDINATE_DIFF_Y
				&&
				(cnt[i]["cxy"].y / cnt[j]["cxy"].y) < MAX_COORDINATE_DIFF_Y
				)
			{
				/*rectangle(drawing, cnt[i]["tl"], cnt[i]["br"], Scalar(0, 255, 0), 1, LINE_8, 0);
				rectangle(drawing, cnt[j]["tl"], cnt[j]["br"], Scalar(0,255,0), 1, LINE_8, 0);
				cout << "거리 : " << (cnt[i]["cxy"].x - cnt[j]["cxy"].x) / rect_width << endl;
				cout << "tl : " << cnt[j]["tl"] << endl << "br : " << cnt[j]["br"] << endl;
				cout << j << "번쨰 영역 크기: " << ((cnt[j]["br"] - cnt[j]["tl"]).x* (cnt[j]["br"] - cnt[j]["tl"]).y) << endl;*/


				tocnt.insert(pair<string, Point_<int>>("tl", cnt[j]["tl"]));
				tocnt.insert(pair<string, Point_<int>>("br", cnt[j]["br"]));
				before_result.push_back(tocnt);
				tocnt.clear();
				//before_result.push_back({ cnt[j]["tl"], cnt[j]["br"] });
			}

		}

		if (before_result.size() < LIST_LEN) {
			before_result.clear();
			continue;
		}
		else {
			tocnt.insert(pair<string, Point_<int>>("tl", cnt[i]["tl"]));
			tocnt.insert(pair<string, Point_<int>>("br", cnt[i]["br"]));
			before_result.insert(before_result.begin(), tocnt);
			/*for (auto a : before_result) {
				rectangle(drawing, a["tl"], a["br"], Scalar(0, 0, 255), 1, LINE_8, 0);
			}*/

			tocnt.clear();
			break;
		}


	}
	return before_result;
}

void Division_license::write_roi_file(Mat & imgs_gray, vector < map<string, Point_ <int> > > & result_contour_list, string write_path) {
	vector <Rect> roi;
	Point_ <int> start_point;
	Point_ <int> end_point;

	//for (auto a : result_contour_list) {
	//	if (a.size() == 0) {
	//		continue;
	//	}
	//	else if (a.size() <= 4) {
	//		//좌측과 위는 2/3 정도 더 넓게. 우측과 아래는 한 변의 길이만큼만.
	//		//start_point = Point_ <int>((a[0]["tl"].x - (int)((a[a.size() - 1]["br"].x - a[0]["tl"].x) * 2 / 3)), (a[0]["tl"].y - (int)(a[a.size() - 1]["br"].y - a[0]["tl"].y) * 2 / 3));
	//		//end_point = Point_ <int>((a[a.size() - 1]["br"].x * 2 - a[0]["tl"].x), (a[a.size() - 1]["br"].y * 2 - a[0]["tl"].y));
	//		start_point = a[0]["tl"];
	//		end_point = a[a.size() - 1]["br"];
	//	}
	//	else {
	//		start_point = a[0]["tl"];
	//		end_point = a[a.size() - 1]["br"];

	//	}

	//	roi.push_back(Rect(start_point, end_point));
	//}
	int x = 0;
	cout << roi.size() << endl;

	map<string, Mat>::iterator iter;
	//for (iter = imgs_gray.begin(); iter != imgs_gray.end(); iter++) {
	//	cout << "x : " << x << endl;
	//	cout << "tl : " << roi[x].tl() << endl << "br : " << roi[x].br() << endl;
	//	imwrite(write_path + iter->first + ".jpg", imgs_gray[iter->first](roi[x]));
	//	//x++;
	//}
}