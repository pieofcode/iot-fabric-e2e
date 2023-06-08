using System;
using System.IO;
using System.Linq;
using System.Text;
using System.Text.Json;
using System.Threading;
using System.Threading.Tasks;
using System.Collections.Generic;
using Faker;
using Microsoft.Azure.Devices.Client;
using DataModels;

namespace Emulator
{
    class Program
    {
        private static string s_DeviceId;
        private static string s_GatewayId;

        private static string s_DataModel;
        private static string s_Properties;
        private static string s_ConnectionString;

        private static int s_frequency = 2000;

        private static int s_counter = 0;

        private static DeviceClient s_DeviceClient;
        // private static readonly TransportType s_TransportType = TransportType.Mqtt;


        static async Task Main(string[] args)
        {
            if (args.Length < 3)
            {
                Console.WriteLine("Missing Command Line Args: [IoT Gateway] and/or [Device Id]");
                Environment.Exit(1);
            }


            // Read the connection string from the file
            s_GatewayId = args[0];
            s_DeviceId = args[1];
            s_DataModel = args[2];
            if (args.Length > 3)
            {
                s_Properties = args[3];
            }

            s_ConnectionString = File.ReadAllText(string.Format("../Devices/{0}/{1}.txt", args[0], args[1]));

            Console.WriteLine("Fetching the device connection string for: {0}", s_DeviceId);
            Console.WriteLine(s_ConnectionString);
            ValidateConnectionString(s_ConnectionString);


            // Create a Device client
            s_DeviceClient = DeviceClient.CreateFromConnectionString(s_ConnectionString);

            Console.WriteLine("Press Ctrl + C to quit the emulator...");

            using var cts = new CancellationTokenSource();
            Console.CancelKeyPress += (sender, eventArgs) =>
            {
                eventArgs.Cancel = true;
                cts.Cancel();
                Console.WriteLine("Stopping the device emulator...");
            };

            //Extract property values
            var properties = new Dictionary<string, string>();
            properties.Add("id", s_DeviceId);
            if (s_Properties != null)
            {
                var propTokens = s_Properties.Split('|');
                foreach (var item in propTokens)
                {
                    var prop = item.Split(':');
                    properties.Add(prop[0], prop[1]);
                }
            }
            Console.WriteLine($"Properties: {properties.Count}");

            if (properties.ContainsKey("frequency"))
            {
                Console.WriteLine($"Overriding the frequency: {properties["frequency"]}");
                int freq;
                var success = int.TryParse(properties["frequency"], out freq);
                if (success)
                {
                    Console.WriteLine($"Setting the frequency: {properties["frequency"]} sec");
                    s_frequency = freq * 1000;
                }
            }

            //Create a datamodel instance based on the args
            var datamodel = MessageProducer.GetDataModel(s_GatewayId, s_DeviceId, s_DataModel, properties);

            await SendDeviceToCloudMessageAsync(cts.Token, datamodel);


            s_DeviceClient.Dispose();

        }

        private static async Task SendDeviceToCloudMessageAsync(CancellationToken ct, BaseDataModel datamodel)
        {

            while (!ct.IsCancellationRequested)
            {
                var strMessages = datamodel.GenerateTelemetry();
                StringBuilder sb = new StringBuilder();
                if (strMessages.Count > 1)
                {
                    IList<Message> messages = new List<Message>();

                    foreach (var item in strMessages)
                    {
                        messages.Add(BuildDeviceMessage(item));
                        sb.AppendLine($"{s_counter} > {DateTime.Now} > {item}");
                    }
                    await s_DeviceClient.SendEventBatchAsync(messages);
                    s_counter++;
                    Console.WriteLine(sb.ToString());

                }
                else
                {
                    var message = BuildDeviceMessage(strMessages[0]);
                    await s_DeviceClient.SendEventAsync(message);
                    s_counter++;
                    Console.WriteLine($"{s_counter} > {DateTime.Now} > {strMessages[0]}");

                }

                // var messageType = "Telemetry";
                // message.Properties.Add("messageType", messageType);
                // message.Properties.Add("schema", "PaintEvent");

                // Console.WriteLine($"{DateTime.Now} > Sending Message: {messageBody}");
                sb.Clear();
                await Task.Delay(s_frequency);
            }
        }

        private static void ValidateConnectionString(string connStr)
        {
            try
            {
                var cs = IotHubConnectionStringBuilder.Create(connStr);
                s_ConnectionString = cs.ToString();
            }
            catch (Exception)
            {
                Console.WriteLine($"Error: Unrecognized Parameter - {connStr}");
                Environment.Exit(1);
            }
        }

        private static Message BuildDeviceMessage(string messageBody)
        {
            var message = new Message(Encoding.ASCII.GetBytes(messageBody))
            {
                ContentType = "application/json",
                ContentEncoding = "utf-8"
            };

            return message;
        }
    }


}
