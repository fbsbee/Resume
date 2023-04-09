package com.restore.visualization;

import android.content.Context;
import android.opengl.GLSurfaceView;
import android.opengl.Matrix;

import com.opencsv.CSVReader;

import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.nio.FloatBuffer;

import java.util.ArrayList;

import javax.microedition.khronos.opengles.GL10;

import static android.opengl.GLES20.*;

// 화면 그리는 클래스
class MyGLSurfaceView extends GLSurfaceView {

    private final MyGLRenderer mRenderer;

    public MyGLSurfaceView(Context context){
        super(context);

        // OpenGL ES 2.0 context를 생성합니다.
        setEGLContextClientVersion(2);

        mRenderer = new MyGLRenderer();

        // GLSurfaceView에 그래픽 객체를 그리는 처리를 하는 renderer를 설정합니다.
        setRenderer(mRenderer);

        //Surface가 생성될때와 GLSurfaceView클래스의 requestRender 메소드가 호출될때에만
        //화면을 다시 그리게 됩니다.
        setRenderMode(GLSurfaceView.RENDERMODE_WHEN_DIRTY);
    }

}

// 데이터 그리는 클래스
class MyGLRenderer implements GLSurfaceView.Renderer {

    //GLSurfaceView가 생성되었을때 한번 호출되는 메소드입니다.
    //OpenGL 환경 설정, OpenGL 그래픽 객체 초기화 등과 같은 처리를 할때 사용됩니다.
    private Human human;
    //GLSurfaceView가 다시 그려질때 마다 호출되는 메소드입니다.

    private final float[] mMVPMatrix = new float[16];
    private final float[] mProjectionMatrix = new float[16];
    private final float[] mViewMatrix = new float[16];
    public void onDrawFrame(GL10 unused) {
        //glClearColor에서 설정한 값으로 color buffer를 클리어합니다.

        //카메라 위치를 나타내는 Camera view matirx를 정의
//        Matrix.setLookAtM(mViewMatrix, 0, 3, 0, -1, 0f, 0.4f, 0f, 0f, 0.5f, 0f); // 2로 나누기만 할 때 쓰는 카메라뷰
        Matrix.setLookAtM(mViewMatrix, 0, 3, 0, -1, 0f, 0.4f, 0f, 0f, 0.5f, 0f); // tanh 쓸때 사용하는 카메라 시점
        //projection matrix와 camera view matrix를 곱하여 mMVPMatrix 변수에 저장
        Matrix.multiplyMM(mMVPMatrix, 0, mProjectionMatrix, 0, mViewMatrix, 0);

        glClear(GL_COLOR_BUFFER_BIT);
        // 버퍼에 데이터 저장 및 그리기
        human.data_input();
        human.draw(mMVPMatrix);
    }

    public static int loadShader(int type, String shaderCode){

        // 다음 2가지 타입 중 하나로 shader객체를 생성한다.
        // vertex shader type (GL_VERTEX_SHADER)
        // 또는 fragment shader type (GL_FRAGMENT_SHADER)
        int shader = glCreateShader(type);

        // shader객체에 shader source code를 로드합니다.
        glShaderSource(shader, shaderCode);

        //shader객체를 컴파일 합니다.
        glCompileShader(shader);

        return shader;
    }

    @Override
    public void onSurfaceCreated(GL10 gl10, javax.microedition.khronos.egl.EGLConfig eglConfig) {
        //shape가 정의된 Triangle 클래스의 인스턴스를 생성합니다.
        human = new Human();
        human.add_data2humanCoords();

        //color buffer를 클리어할 때 사용할 색을 지정합니다.
        //red, green, blue, alpha 순으로 0~1사이의 값을 지정합니다.
        //여기에서는 검은색으로 지정하고 있습니다.
        glClearColor(0.0f, 0.0f, 0.0f, 1.0f);
    }

    //GLSurfaceView의 크기 변경 또는 디바이스 화면의 방향 전환 등으로 인해
    //GLSurfaceView의 geometry가 바뀔때 호출되는 메소드입니다.
    public void onSurfaceChanged(GL10 unused, int width, int height) {
        //viewport를 설정합니다.
        //viewport rectangle의 왼쪽 아래를 (0,0)으로 지정하고
        //viewport의 width와 height를 지정합니다.
        glViewport(0, 0, width, height);
        //GLSurfaceView 너비와 높이 사이의 비율을 계산합니다.
        float ratio = (float) width / height;

        //3차원 공간의 점을 2차원 화면에 보여주기 위해 사용되는 projection matrix를 정의
        Matrix.frustumM(mProjectionMatrix, 0, -ratio, ratio, -1, 1, 3, 7);
    }
}

// csv 파일 데이터 넣고 그리는 클래스
class Human {

    private final String vertexShaderCode =

            "uniform mat4 uMVPMatrix;" +
                    "attribute vec4 vPosition;" +
                    "void main() {" +
                    "  gl_Position = uMVPMatrix * vPosition;" +
                    "}";

    private final String fragmentShaderCode =
            "precision mediump float;" +
                    "uniform vec4 vColor;" +
                    "void main() {" +
                    "  gl_FragColor = vColor;" +
                    "}";

    //float buffer 타입으로 vertexBuffer를 선언합니다.
    private FloatBuffer vertexBuffer;

    //0. float 배열에 삼각형의 vertex를 위한 좌표를 넣습니다.
    static final int COORDS_PER_VERTEX = 3;

    //red, green, blue, alpha 값을 float 배열 color에 넣습니다.
    float color[] = { 0.803922f, 0.788235f, 0.788235f, 1.0f };

    private int mProgram;

    public ArrayList<float[]> humanCoords = new ArrayList<>();
    static CSVReader reader;

    static int select = 0;
    static boolean play = false;
    static int array_size;

    public void add_data2humanCoords(){
        int i = 0;
        String[] nextLine;
        try {
            while ((nextLine = reader.readNext()) != null) {
                humanCoords.add(new float[nextLine.length]);
                for (int j = 1; j < nextLine.length; j++) {
//                    humanCoords.get(i)[j-1] = (float)Math.tanh(Float.parseFloat(nextLine[j]));
//                    humanCoords.get(i)[j-1] = (float)Math.log(Float.parseFloat(nextLine[j]));
//                    humanCoords.get(i)[j-1] = Float.parseFloat(nextLine[j]) / 2;
                    humanCoords.get(i)[j-1] = (float)Math.tanh(Float.parseFloat(nextLine[j])) / 2;
                }
                i++;
            }
            array_size = humanCoords.size();
        }catch (Exception e){
            System.out.println(e);
        }
    }

    public void data_input(){
        ByteBuffer bb = ByteBuffer.allocateDirect(
                // (number of coordinate values * 4 bytes per float)
                humanCoords.size() * humanCoords.get(0).length * Float.BYTES);

        //2. ByteBuffer에서 사용할 엔디안을 지정합니다.
        //버퍼의 byte order로써 디바이스 하드웨어의 native byte order를 사용
        bb.order(ByteOrder.nativeOrder());

        //3. ByteBuffer를 FloatBuffer로 변환합니다.
        vertexBuffer = bb.asFloatBuffer();

        //4. float 배열에 정의된 좌표들을 FloatBuffer에 저장합니다.
        // 사이즈보다 크면 humanCoords에 있는 마지막값 불러오기
        if(select >= humanCoords.size()){
            select = array_size - 1 ;
            // 재생 중이면 재생 중지.
            if(play) {
                play = false;
            }
            vertexBuffer.put(humanCoords.get(select));
        // 0보다 작으면 humanCoords에 있는 0번째 값 불러오기
        }else if(select < 0){
            select = 0;
            vertexBuffer.put(humanCoords.get(select));
        // humanCoords에 있는 값 불러오기.
        }else{
            vertexBuffer.put(humanCoords.get(select));
        }

        //5. 읽어올 버퍼의 위치를 0으로 설정한다. 첫번째 좌표부터 읽어오게됨
        vertexBuffer.position(0);

        //vertex shader 타입의 객체를 생성하여 vertexShaderCode에 저장된 소스코드를 로드한 후,
        //   컴파일합니다.
        int vertexShader = MyGLRenderer.loadShader(GL_VERTEX_SHADER,
                vertexShaderCode);

        //fragment shader 타입의 객체를 생성하여 fragmentShaderCode에 저장된 소스코드를 로드한 후,
        //  컴파일합니다.
        int fragmentShader = MyGLRenderer.loadShader(GL_FRAGMENT_SHADER,
                fragmentShaderCode);

        // Program 객체를 생성한다.
        mProgram = glCreateProgram();

        // vertex shader를 program 객체에 추가
        glAttachShader(mProgram, vertexShader);

        // fragment shader를 program 객체에 추가
        glAttachShader(mProgram, fragmentShader);

        // program객체를 OpenGL에 연결한다. program에 추가된 shader들이 OpenGL에 연결된다.
        glLinkProgram(mProgram);

    }

    private int mPositionHandle;
    private int mColorHandle;

    private final int vertexStride = COORDS_PER_VERTEX * 4; // 4 bytes per vertex
    private int mMVPMatrixHandle;
    public void draw(float[] mvpMatrix) {
        //렌더링 상태(Rendering State)의 일부분으로 program을 추가한다.
        glUseProgram(mProgram);

        // program 객체로부터 vertex shader의'vPosition 멤버에 대한 핸들을 가져옴
        mPositionHandle = glGetAttribLocation(mProgram, "vPosition");

        // human vertex 속성을 활성화 시켜야 렌더링시 반영되서 그려짐
        glEnableVertexAttribArray(mPositionHandle);

        // human vertex 속성을 vertexBuffer에 저장되어 있는 vertex 좌표들로 정의한다.
        glVertexAttribPointer(mPositionHandle, COORDS_PER_VERTEX,
                GL_FLOAT, false,
                vertexStride, vertexBuffer);

        // program 객체로부터 fragment shader의 vColor 멤버에 대한 핸들을 가져옴
        mColorHandle = glGetUniformLocation(mProgram, "vColor");

        //human 렌더링시 사용할 색으로 color변수에 정의한 값을 사용한다.
        glUniform4fv(mColorHandle, 1, color, 0);

        //vertex 갯수만큼 human을 렌더링한다.
        final int vertexCount = humanCoords.size()*humanCoords.get(0).length / COORDS_PER_VERTEX;

        //program 객체로부터 vertex shader 타입의 객체에 정의된 uMVPMatrix에 대한 핸들을 획득합니다.
        mMVPMatrixHandle = glGetUniformLocation(mProgram, "uMVPMatrix");

        //projection matrix와 camera view matrix를 곱하여 얻어진  mMVPMatrix 변수의 값을
        // vertex shader 객체에 선언된 uMVPMatrix 멤버에게로 넘겨줍니다.
        glUniformMatrix4fv(mMVPMatrixHandle, 1, false, mvpMatrix, 0);

        glDrawArrays(GL_POINTS, 0, vertexCount);
        glLineWidth(28);

        //vertex 속성을 비활성화 한다.
        glDisableVertexAttribArray(mPositionHandle);
    }
}
