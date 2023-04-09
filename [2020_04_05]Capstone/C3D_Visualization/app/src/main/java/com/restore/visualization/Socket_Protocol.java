package com.restore.visualization;

import android.util.Pair;

import java.io.BufferedInputStream;
import java.io.BufferedOutputStream;
import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.net.Socket;
import java.net.SocketTimeoutException;
import java.net.UnknownHostException;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.util.ArrayList;

class Transfer_Data extends Thread{

    private final int DATA_SEND = 2<<12;
    private final String ip = "su-surface.asuscomm.com";
//    private final String ip = "192.168.219.106";
    private final int port = 9999;
    private ArrayList<Pair<BufferedInputStream, BufferedOutputStream>> files = new ArrayList<>();
//    파일 두개를 전송하기 위한 작업시도.
//    private ArrayList<Pair<BufferedInputStream, Pair<BufferedOutputStream, BufferedOutputStream>>> files = new ArrayList<>();
//    public void append_data(Pair<BufferedInputStream, Pair<BufferedOutputStream, BufferedOutputStream>> file){
//        this.files.add(file);
//    } // end append_data
    public void append_data(Pair<BufferedInputStream, BufferedOutputStream> file){
        this.files.add(file);
    } // end append_data

    @Override
    public void run(){
        try{
            for(Pair<BufferedInputStream, BufferedOutputStream> file : files){
                Socket client = new Socket(ip, port);
                Socket_Protocol sp = new Socket_Protocol(DATA_SEND, ip, port, file.first, file.second, client);
                sp.start();
            }
//            파일 두개를 전송하기 위한 작업시도.
//            for(Pair<BufferedInputStream, Pair<BufferedOutputStream, BufferedOutputStream>> file : files){
//                Socket client = new Socket(ip, port);
//                Socket_Protocol sp = new Socket_Protocol(DATA_SEND, ip, port, file.first, file.second.first, file.second.second, client);
//                sp.start();
//            }
        }catch (UnknownHostException e){
            System.out.println("host 이름 식별 불가능");
            e.printStackTrace();
        }catch (SocketTimeoutException e){
            System.out.println("시간 초과");
            e.printStackTrace();
        }catch (Exception e){
            System.out.println("오류났어요");
            e.printStackTrace();
        }
    } // end run()

} // end class Transfer_Data

// 소켓 연결할 클라이언트 Thread 생성
public class Socket_Protocol extends Thread {
    private int DATA_SEND;
    private String ip;
    private int port;
    private BufferedInputStream bis;
    private BufferedOutputStream bos;

//    파일 두개를 전송하기 위한 작업시도.
//    private BufferedOutputStream bos_origin;
//    private BufferedOutputStream bos_modified;
//
//    Socket_Protocol(int DATA_SEND, String ip, int port, BufferedInputStream bis,
//                    BufferedOutputStream bos_origin, BufferedOutputStream bos_modified, Socket client)
//    {
//        this.DATA_SEND = DATA_SEND;
//        this.ip = ip;
//        this.port = port;
//        this.bis  = bis;
//        this.bos_origin = bos_origin;
//        this.bos_modified = bos_modified;
//        this.run(client);
//    } // end 생성자

    Socket_Protocol(int DATA_SEND, String ip, int port, BufferedInputStream bis, BufferedOutputStream bos, Socket client){
        this.DATA_SEND = DATA_SEND;
        this.ip = ip;
        this.port = port;
        this.bis  = bis;
        this.bos = bos;
        this.run(client);
    } // end 생성자

    public void run(Socket client) {
        try {
            BufferedOutputStream sender = new BufferedOutputStream(
                    client.getOutputStream());

            DataOutputStream dos = new DataOutputStream(sender);

            byte[] buff = new byte[this.bis.available()];

            // 파일 크기를 구해서 전송
            dos.write(buff, 0, this.bis.read(buff));

            // 파일 전송 끝난걸 알림
            client.shutdownOutput();
            System.out.println("송신완료");
            this.bis.close();
//            bis.close();

            // 데이터 파일 수신
            BufferedInputStream receiver = new BufferedInputStream(client.getInputStream());
            DataInputStream dis_recv = new DataInputStream(receiver);

            // buffer 생성
            byte[] buf = new byte[DATA_SEND];
            int readdata;

//            파일 두개를 전송하기 위한 작업시도.
//            // 원본 파일
//            // 파일 길이 읽기
//            byte[] data = new byte[4];
//            dis_recv.read(data, 0, 4);
//
//            ByteBuffer b = ByteBuffer.wrap(data);
//            b.order(ByteOrder.LITTLE_ENDIAN);
//            int length = b.getInt();
//            System.out.println("원본 데이터 크기 : " + length);
//
////          원본 파일 쓰기
//            while ((readdata = dis_recv.read(buf)) > 0) {
//
//                calc += readdata;
//                if(length < calc){
//                    this.bos_origin.write(buf, 0, length - calc + readdata);
//                    System.out.println("마지막 내려받은 데이터 크기 : " + (length - (calc - readdata) ));
//                    System.out.println("readdata : " + readdata);
//                    System.out.println("여태 내려받은 데이터 크기 : " + calc);
//                    this.bos_origin.flush();
//                    break;
//                }
//                this.bos_origin.write(buf,0,readdata);
//                this.bos_origin.flush();
//            }
//
//            // 수정된 파일
//            // 파일 길이 읽기
////            data = new byte[4];
////            dis_recv.read(data, 0, 4);
////
////            b = ByteBuffer.wrap(data);
////            b.order(ByteOrder.LITTLE_ENDIAN);
////            length = b.getInt();
////
////            System.out.println("수정된 데이터 크기 : " + length);
//            buf = new byte[DATA_SEND];
//            readdata = 0;
//            // 수정된 파일 쓰기
//            while ((readdata = dis_recv.read(buf)) > 0) {
//                this.bos_modified.write(buf,0, readdata);
//                this.bos_modified.flush();
//            }
//
//            this.bos_modified.flush();
//
//            dis_recv.close();
//            this.bos_origin.close();
//            this.bos_modified.close();
//
            // 파일 쓰기
            while ((readdata = dis_recv.read(buf)) > 0) {
                this.bos.write(buf,0,readdata);
                this.bos.flush();
            }
            this.bos.flush();

            dis_recv.close();
            this.bos.close();
            dos.close();
            client.close();   //socket 닫아줌
            System.out.println("수신 완료");

        } catch (Exception e) {
            e.printStackTrace();
        }
    } // end run
} // end Socket_Protocol
