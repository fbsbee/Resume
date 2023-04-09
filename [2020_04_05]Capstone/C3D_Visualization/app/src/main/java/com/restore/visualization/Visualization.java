package com.restore.visualization;

import android.app.Activity;

import android.content.Intent;
import android.net.Uri;
import android.opengl.GLSurfaceView;
import android.os.Bundle;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.ImageButton;

import com.opencsv.CSVReader;

import java.io.InputStream;
import java.io.InputStreamReader;

// 화면 넘어오는 클래스
public class Visualization extends Activity {

    static final int REQUEST_CODE_FOR_ON_BTN_FILE_SELECT = 2;
    private GLSurfaceView mGLView;
    final Human hm = new Human();

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        // GLSurfaceView 인스턴스를 생성하여 Activity를 위한 Content View로 설정한다.
        mGLView = new MyGLSurfaceView(this);
        setContentView(mGLView);

        // 뷰 덮어쓰기
        View v = getLayoutInflater().inflate(R.layout.opengl_view, null);
        addContentView(v, new ViewGroup.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT));

        final Button btn_previous, btn_next, btn_play;
        // 이전 버튼, 플레이버튼 선언
        btn_play = findViewById(R.id.btn_play);
        btn_previous = findViewById(R.id.btn_previous);

        btn_previous.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                hm.select -= 1;
                if (hm.play == true) {
                    hm.play = false;
                }
                mGLView.requestRender();
            }
        });

        // 다음 버튼
        btn_next = findViewById(R.id.btn_next);
        btn_next.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                hm.select += 1;
                if (hm.play == true) {
                    hm.play = false;
                }
                mGLView.requestRender();
            }
        });

        // 재생 버튼
        btn_play.setOnClickListener(new View.OnClickListener() {

            @Override
            public void onClick(View view) {
                if (hm.play == true){
                    hm.play = false;
                }else{
                    hm.play = true;
                }
                new Thread(){
                    public void run() { // 스레드에게 수행시킬 동작들 구현
                        while(hm.play){
                            hm.select += 1;
                            try {
                                Thread.sleep(50); // 0.05초
                            } catch (InterruptedException e) {
                                e.printStackTrace();
                            }
                            mGLView.requestRender();
                        }
                    }
                }.start(); // end Thread
            } // end btn_play

        });

        // 이미지 버튼들
        ImageButton btn_restore, btn_file_select;
        // 초기화 버튼
        btn_restore = findViewById(R.id.btn_restore);
        btn_restore.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                hm.play = false;
                hm.select = 0;
                mGLView.requestRender();
            }
        }); // end btn_restore

        btn_file_select = findViewById(R.id.btn_file_select);
        btn_file_select.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                hm.play = false;
                // 0으로 안하면 멈춘 프레임 그대로 다른 파일에서 가져다가 비교 가능하긴 한데.
                // 편한대로
//                hm.select = 0;

                Intent files_intent = new Intent(Intent.ACTION_OPEN_DOCUMENT);
                files_intent.addCategory(Intent.CATEGORY_OPENABLE);
                files_intent.setType("*/*");
//                setResult(REQUEST_CODE_FOR_ON_BTN_FILE_SELECT, files_intent);
                startActivityForResult(files_intent, REQUEST_CODE_FOR_ON_BTN_FILE_SELECT);
            }
        }); // end btn_file_select

    }// end onCreate

    @Override
    public void onBackPressed() {
        super.onBackPressed();
        hm.select = 0;
        hm.play = false;

    } // end on BackPressed

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if (requestCode == REQUEST_CODE_FOR_ON_BTN_FILE_SELECT){
            if (resultCode == RESULT_OK) {
                Uri uri = data.getData();
                // 파일 읽기
                try{
                    InputStream fis = getContentResolver().openInputStream(uri);
                    InputStreamReader isr = new InputStreamReader(fis);
                    CSVReader reader = new CSVReader(isr);
                    Human mhuman = new Human();
                    mhuman.reader = reader;

//                    Intent intent = new Intent(getApplicationContext(), this.getClass());
//
//                    startActivity(intent);
                    Intent intent = new Intent(getApplicationContext(), this.getClass());
//                    intent.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TASK | Intent.FLAG_ACTIVITY_CLEAR_TOP);
//                    intent.setFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP | Intent.FLAG_ACTIVITY_SINGLE_TOP);
                    intent.setFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP | Intent.FLAG_ACTIVITY_NEW_TASK);
                    startActivity(intent);


                }catch(Exception e){
                    System.out.println(e);
                }
            }else{
            } // end 메뉴 버튼에서 데이터 선택했을 때

        }else{
        }

    } // end onActivityResult
} // end Visualization class
