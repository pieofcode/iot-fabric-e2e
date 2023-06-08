using System;
using System.IO;
using System.Linq;
using System.Text;
using System.Collections.Generic;
using System.Text.Json;
using System.Threading;
using System.Threading.Tasks;
using Bogus;

namespace DataModels
{
    public class LocationSensorModel : BaseDataModel
    {
        // Report sensor location (Within CA :))
        private double longitude;
        private double latitude;
        private static int s_EventId;

        static LocationSensorModel()
        {
            s_EventId = 1;
        }
        public LocationSensorModel(string gatewayId, string deviceId, Dictionary<string, string> properties = null) : base(gatewayId, deviceId, properties)
        {
            var rand = new Random();
            longitude = 48 + (rand.NextDouble() * 10);
            latitude = -80 - (rand.NextDouble() * 10);
        }

        public override IList<string> GenerateTelemetry()
        {
            var strMessages = new List<string>();

            double minTemperature = 20;
            double minHumidity = 60;

            var rand = new Random();

            double currentTemperature = minTemperature + rand.NextDouble() * 15;
            double currentHumidity = minHumidity + rand.NextDouble() * 20;

            string messageBody = JsonSerializer.Serialize(
                new
                {
                    eventDate = DateTime.UtcNow,
                    deviceId = this.DeviceId,
                    gatewayId = this.GatewayId,
                    messageId = s_EventId++,
                    temperature = currentTemperature,
                    humidity = currentHumidity,
                    longitude = longitude,
                    latitude = latitude
                }
            );

            strMessages.Add(messageBody);

            var lowBattery = rand.NextDouble() > 0.8 ? true : false;
            var tempAlert = currentTemperature > 30 ? true : false;
            if (lowBattery || tempAlert)
            {
                string tamperMessageBody = JsonSerializer.Serialize(
                    new
                    {
                        eventDate = DateTime.UtcNow,
                        deviceId = this.DeviceId,
                        gatewayId = this.GatewayId,
                        tempAlert = tempAlert,
                        lowBattery = lowBattery
                    }
                );
                strMessages.Add(tamperMessageBody);
            }

            return strMessages;
        }

    }
}
