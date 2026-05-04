using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using System.Net;
using System.Net.Sockets;
using System.Threading;
using System.Text;

public class UDPVideoServer : MonoBehaviour
{
    public int listenPort = 5006;
    public int maxPacketSize = 60000;
    public Renderer targetRenderer;
    private UdpClient udpClient;
    private UdpClient sendClient;
    private Thread receiveThread;
    private bool running = false;
    private byte[] frameBuffer;
    private int expectedFrameSize = 0;
    private int receivedBytes = 0;
    private Queue<byte[]> frameQueue = new Queue<byte[]>();
    private Texture2D texture;
    private IPEndPoint pythonEP;

    void Start()
    {
        if (targetRenderer == null)
            targetRenderer = GetComponent<Renderer>();

        texture = new Texture2D(2, 2);
        targetRenderer.material.mainTexture = texture;

        udpClient = new UdpClient();
        udpClient.Client.SetSocketOption(SocketOptionLevel.Socket, SocketOptionName.ReuseAddress, true);
        udpClient.Client.Bind(new IPEndPoint(IPAddress.Any, listenPort));
        sendClient = new UdpClient();

        running = true;

        receiveThread = new Thread(ReceiveData);
        receiveThread.IsBackground = true;
        receiveThread.Start();

        StartCoroutine(SendReadyPacket());
    }

    IEnumerator SendReadyPacket()
    {
        int broadcastPort = 5007;
        IPEndPoint broadcastEP = new IPEndPoint(IPAddress.Broadcast, broadcastPort);
        byte[] readyMsg = Encoding.UTF8.GetBytes("READY");

        while (pythonEP == null)
        {
            sendClient.Send(readyMsg, readyMsg.Length, broadcastEP);
            Debug.Log("Sending READY broadcast...");
            yield return new WaitForSeconds(1f); 
        }
        sendClient.Send(readyMsg, readyMsg.Length, broadcastEP);
        Debug.Log("READY Received...");
    }

    void ReceiveData()
    {
        IPEndPoint remoteEP = new IPEndPoint(IPAddress.Any, listenPort);

        while (running)
        {
            try
            {
                byte[] data = udpClient.Receive(ref remoteEP);

                if (pythonEP == null)
                {
                    pythonEP = remoteEP;
                    Debug.Log("Connected to Python: " + pythonEP.ToString());
                    continue;
                }

                if (data.Length == 4)
                {
                    expectedFrameSize = System.BitConverter.ToInt32(data, 0);
                    frameBuffer = new byte[expectedFrameSize];
                    receivedBytes = 0;
                    continue;
                }

                int copyLength = Mathf.Min(data.Length, expectedFrameSize - receivedBytes);
                if (frameBuffer == null)
                {
                    Debug.LogWarning("Received video data but frameBuffer is null. Packet size: " + data.Length);
                    continue;
                }
                System.Buffer.BlockCopy(data, 0, frameBuffer, receivedBytes, copyLength);
                receivedBytes += copyLength;

                if (receivedBytes >= expectedFrameSize)
                {
                    lock (frameQueue)
                    {
                        byte[] frameCopy = new byte[expectedFrameSize];
                        System.Buffer.BlockCopy(frameBuffer, 0, frameCopy, 0, expectedFrameSize);
                        frameQueue.Enqueue(frameCopy);
                    }

                    receivedBytes = 0;
                }
            }
            catch (SocketException ex)
            {
                Debug.LogWarning("Socket exception: " + ex.Message);
            }
        }
    }

    void Update()
    {
        lock (frameQueue)
        {
            while (frameQueue.Count > 0)
            {
                byte[] frameData = frameQueue.Dequeue();

                if (texture == null)
                    texture = new Texture2D(2, 2);

                texture.LoadImage(frameData);
                bool success = texture.LoadImage(frameData);
                if (!success)
                {
                    Debug.LogWarning("Failed to load image, expected " + expectedFrameSize + " bytes, received " + 
                    receivedBytes + " bytes.");
                }
                
                texture.Apply();
            }
        }
    }

    void OnApplicationQuit()
    {
        running = false;

        if (receiveThread != null && receiveThread.IsAlive)
        {
            receiveThread.Abort();
        }

        if (udpClient != null) 
        {
            udpClient.Close();
        }

        if (sendClient != null) 
        {
            sendClient.Close();
        }
    }
}