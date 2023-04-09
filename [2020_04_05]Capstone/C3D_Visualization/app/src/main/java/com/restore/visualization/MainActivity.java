package com.restore.visualization;
import android.Manifest;
import android.content.ClipData;
import android.content.ContentResolver;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.os.StrictMode;
import android.provider.MediaStore;
import android.util.Pair;
import android.view.View;
import android.widget.ImageButton;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.appcompat.app.AppCompatActivity;

import com.opencsv.CSVReader;

import java.io.BufferedInputStream;
import java.io.BufferedOutputStream;
import java.io.File;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStream;

public class MainActivity extends AppCompatActivity {

    static final int REQUEST_CODE_FOR_ON_BTN_UPLOAD = 1;
    static final int REQUEST_CODE_FOR_ON_BTN_VISUALIZATION = 2;
    // 권한 부여 생성
    String[] permission_list = {
            Manifest.permission.WRITE_EXTERNAL_STORAGE,
            Manifest.permission.READ_EXTERNAL_STORAGE,

    };
    private long backKeyClickTime = 0;

    @Override
    protected void onCreate(@Nullable Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.main);
        checkPermission();
        ImageButton btn_visualization, btn_upload;

        int SDK_INT = android.os.Build.VERSION.SDK_INT;
        if (SDK_INT > 8){
            StrictMode.ThreadPolicy policy = new StrictMode.ThreadPolicy.Builder().permitAll().build();
            StrictMode.setThreadPolicy(policy);
        }

        // 시각화 버튼 이벤트 활성화
        btn_visualization = findViewById(R.id.btn_visualization);
        btn_visualization.setOnClickListener((new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                Intent files_intent = new Intent(Intent.ACTION_OPEN_DOCUMENT);
                files_intent.addCategory(Intent.CATEGORY_OPENABLE);
                files_intent.setType("*/*");
                startActivityForResult(files_intent, REQUEST_CODE_FOR_ON_BTN_VISUALIZATION);
            }
        }));

        // 업로드 버튼 이벤트 활성화
        btn_upload = findViewById(R.id.btn_upload);
        btn_upload.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
//                Intent files_intent = new Intent(Intent.ACTION_CREATE_DOCUMENT);
                Intent files_intent = new Intent(Intent.ACTION_OPEN_DOCUMENT);
                files_intent.putExtra(Intent.EXTRA_ALLOW_MULTIPLE, true);
                files_intent.addCategory(Intent.CATEGORY_OPENABLE);
                files_intent.setType("*/*");
                startActivityForResult(files_intent, REQUEST_CODE_FOR_ON_BTN_UPLOAD);
            }
        });
    } // end onCreate

    // 뒤로가기 이벤트
    public void onBackPressed() {

        if (System.currentTimeMillis() > backKeyClickTime + 2000) {
            backKeyClickTime = System.currentTimeMillis();
            Toast.makeText(this, "뒤로 가기 버튼을 한 번 더 누르면 종료됩니다.", Toast.LENGTH_SHORT).show();
            return;
        }
        if (System.currentTimeMillis() <= backKeyClickTime + 2000) {
            this.finish();
        }
    } // end onBackPressed

    // 저장소 권한 설정
    public void checkPermission(){
        //현재 안드로이드 버전이 6.0미만이면 메서드를 종료한다.
        if(Build.VERSION.SDK_INT < Build.VERSION_CODES.M)
            return;

        for(String permission : permission_list){
            //권한 허용 여부를 확인한다.
            int chk = checkCallingOrSelfPermission(permission);

            if(chk == PackageManager.PERMISSION_DENIED){
                //권한 허용을여부를 확인하는 창을 띄운다
                requestPermissions(permission_list,0);
            }
        }

    }// end checkPermission
    // 저장소 권한 설정
    @Override
    public void onRequestPermissionsResult(int requestCode, @NonNull String[] permissions, @NonNull int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
        if(requestCode==0)
        {
            for(int i=0; i<grantResults.length; i++)
            {
                //허용됬다면
                if(grantResults[i]==PackageManager.PERMISSION_GRANTED){
                }
                else {
                    finish();
                }
            }
        }
    }// end onRequestPermissionsResult

    // intent data 값 받았을 때
    @Override
    protected void onActivityResult(int requestCode, int resultCode, @Nullable Intent data) {
        super.onActivityResult(requestCode, resultCode, data);

        // 업로드 버튼에서 데이터 받았을 때
        if (requestCode == REQUEST_CODE_FOR_ON_BTN_UPLOAD){
            if (resultCode == RESULT_OK){
                // 데이터 하나 선택했을 때
                Uri uri = data.getData();
                // 데이터 여러개 선택했을 때
                ClipData cl_data = data.getClipData();
                // contentResolver 생성
                ContentResolver contentResolver = getContentResolver();

                final Transfer_Data transfer_data = new Transfer_Data();
                if (uri != null) {
                    try{
                        System.out.println("선택한 uri : " + uri);
                        transfer_data.append_data(getBuffer(uri, contentResolver));
                        new Thread(){
                            public void run(){
                                transfer_data.run();
                            }
                        }.start();
                    }catch (Exception e){
                        System.out.println(" 오류 : " + e);
                        System.out.println("데이터 선택 안함");
                    }

                }else if(cl_data != null){ // else로 해도 되지만 상세하게
                    try{
                        for(int i = 0; i< cl_data.getItemCount(); i++){
                            Uri cl_data_uri = cl_data.getItemAt(i).getUri();
                            transfer_data.append_data(getBuffer(cl_data_uri, contentResolver));
                        }
                        new Thread(){
                            public void run(){
                                transfer_data.run();
                            }
                        }.start();

                    }catch (Exception e){
                        System.out.println("오류 : " + e);
                        System.out.println("데이터 선택 안함");
                    }

                } // end else if

            }else{

            }// end 업로드 버튼에서 데이터 선택했을 때

        // 시각화 버튼에서 데이터 받았을 때
        }else if(requestCode == REQUEST_CODE_FOR_ON_BTN_VISUALIZATION){
            if (resultCode == RESULT_OK){
                // 데이터 하나 선택했을 때
                Uri uri = data.getData();
                // 파일 읽기
                try{
                    InputStream fis = getContentResolver().openInputStream(uri);
                    InputStreamReader isr = new InputStreamReader(fis);
                    CSVReader reader = new CSVReader(isr);
                    Human mhuman = new Human();
                    mhuman.reader = reader;

                    Intent intent = new Intent(getApplicationContext(), Visualization.class);
                    startActivity(intent);

                }catch(Exception e){
                    System.out.println(e);
                    System.out.println("파일 못읽었음");
                }
            }else{

            } // end 시각화 버튼에서 데이터 선택했을 때
        } // end 시각화 버튼에서 데이터 받았을 때
        else{

        }

    } // end onActivityResult

    // uri 경로 변환
    public static String getPath(Uri uri){
        String file_name = uri.getPath();
        System.out.println("uri 확인 해야 함 : " + file_name);
        file_name = "/" + file_name.substring(file_name.indexOf(":") + 1);
        return file_name;
    }// end getPath

    // 파일 버퍼 반환
    public Pair<BufferedInputStream, BufferedOutputStream> getBuffer(Uri uri, ContentResolver contentResolver) throws Exception {
        InputStream in = contentResolver.openInputStream(uri);

        String string_uri = getPath(uri);
        File write_uri = new File(string_uri.substring(0, string_uri.lastIndexOf(".")) + "_modified.csv");
        FileOutputStream out = new FileOutputStream(write_uri);

        BufferedInputStream reader = new BufferedInputStream(in);
        BufferedOutputStream writer = new BufferedOutputStream(out);

        return new Pair<>(reader, writer);
    }// end getBuffer

    // 파일 버퍼 반환
//    파일 두개를 전송하기 위한 작업시도.
//    public Pair<BufferedInputStream, Pair<BufferedOutputStream, BufferedOutputStream>> getBuffer(Uri uri, ContentResolver contentResolver) throws Exception {
//
//        InputStream in = contentResolver.openInputStream(uri);
//
//        String string_uri = getPath(uri);
//
////      original data file name
//        File write_uri_origin = new File(string_uri.substring(0, string_uri.lastIndexOf(".")) + "_original.csv");
//        FileOutputStream out_origin = new FileOutputStream(write_uri_origin);
//
////      modified data file name
//        File write_uri_modified = new File(string_uri.substring(0, string_uri.lastIndexOf(".")) + "_modified.csv");
//        FileOutputStream out_modified = new FileOutputStream(write_uri_modified);
//
////        OutputStream out = contentResolver.openOutputStream(write_uri);
////        ParcelFileDescriptor out = contentResolver.openFileDescriptor(write_uri, "w");
//
//        // input stream은 하나만 있어도 됨
//        BufferedInputStream reader = new BufferedInputStream(in);
//
//        BufferedOutputStream writer_origin = new BufferedOutputStream(out_origin);
//        BufferedOutputStream writer_modified = new BufferedOutputStream(out_modified);
//
//        return new Pair<>(reader, new Pair<>(writer_origin, writer_modified));
//
////        return new Pair<>(new Pair<>(reader, writer_origin), new Pair<>(reader, writer_modified));
//    }// end getBuffer

} // end MainActivity
