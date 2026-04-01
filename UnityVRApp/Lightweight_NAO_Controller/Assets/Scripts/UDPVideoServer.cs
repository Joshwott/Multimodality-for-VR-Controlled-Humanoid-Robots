using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using System.Net;
using System.Net.Sockets;
using System.Threading;
using System.Text;

public class UDPVideoServer : MonoBehaviour
{
    [Header("UDP Settings")]
    public int listenPort = 5006;
    public int maxPacketSize = 60000;

    [Header("Display")]
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

    private IPEndPoint clientEP;
    private bool readySent = false;

    void Start()
    {
        if (targetRenderer == null)
            targetRenderer = GetComponent<Renderer>();

        texture = new Texture2D(2, 2);
        targetRenderer.material.mainTexture = texture;

        udpClient = new UdpClient(listenPort);
        sendClient = new UdpClient();
        running = true;

        receiveThread = new Thread(ReceiveData);
        receiveThread.IsBackground = true;
        receiveThread.Start();
    }

    void ReceiveData()
    {
        IPEndPoint remoteEP = new IPEndPoint(IPAddress.Any, listenPort);

        while (running)
        {
            try
            {
                byte[] data = udpClient.Receive(ref remoteEP);

                // Send READY once to first client
                if (!readySent)
                {
                    sendClient.Send(Encoding.UTF8.GetBytes("READY"), 5, remoteEP);
                    clientEP = remoteEP;
                    readySent = true;
                    Debug.Log("Sent READY to client: " + remoteEP.ToString());
                    continue;
                }

                // First 4 bytes: frame size
                if (data.Length == 4)
                {
                    expectedFrameSize = System.BitConverter.ToInt32(data, 0);
                    frameBuffer = new byte[expectedFrameSize];
                    receivedBytes = 0;
                    continue;
                }

                // Copy chunk into buffer
                int copyLength = Mathf.Min(data.Length, expectedFrameSize - receivedBytes);
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
                Debug.Log("Socket exception: " + ex.Message);
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
                texture.LoadImage(frameData);
            }
        }
    }

    void OnApplicationQuit()
    {
        running = false;
        if (receiveThread != null && receiveThread.IsAlive)
            receiveThread.Abort();

        if (udpClient != null) udpClient.Close();
        if (sendClient != null) sendClient.Close();
    }
}