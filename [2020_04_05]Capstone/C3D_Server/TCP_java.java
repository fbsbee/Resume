import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.io.PrintWriter;
import java.net.ServerSocket;
import java.net.Socket;

class TCPServer implements Runnable {
	public static final int ServerPort = 12345;
	// public static final String ServerIP = "192.168.1.223";
	
	@Override
	public void run() {
		try {
			System.out.println("Connecting..");
			ServerSocket serverSocket = new ServerSocket(ServerPort);
			
			while (true) {
				//client 접속 대기
				Socket client = serverSocket.accept();
				System.out.println(client.getInetAddress() + ", " + client.getPort());
				System.out.println("Receving..");
				
				try {
					//client data 수신
					BufferedReader in = new BufferedReader(new InputStreamReader(client.getInputStream()));
					String str = in.readLine();
					System.out.println("Received:" + str + "");
					
					//client data 반환
					PrintWriter out = new PrintWriter(new BufferedWriter(new OutputStreamWriter(client.getOutputStream())), true);
					out.println("Server Received : " + str + "");
					
				} catch (Exception e) {
					System.out.println("Error");
					e.printStackTrace();
				} finally {
					client.close();
					serverSocket.close();
					System.out.println("Done");
				}
			}
		} catch (Exception e) {
			System.out.println("S: Error");
			e.printStackTrace();
		}
	}
	
	public static void main(String[] args) {
		Thread ServerThread = new Thread(new TCPServer());
		ServerThread.start();
	}
}