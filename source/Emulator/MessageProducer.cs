using System;
using System.IO;
using System.Linq;
using System.Text;
using System.Text.Json;
using System.Threading;
using System.Threading.Tasks;
using System.Collections.Generic;
using Bogus;
using DataModels;


using Microsoft.Azure.Devices.Client;

namespace Emulator
{
    internal class MessageProducer
    {

        internal static BaseDataModel GetDataModel(string gatewayId, string deviceId, string datamodel, Dictionary<string, string> args)
        {
            var properties = new Dictionary<string, string>();

            if (!string.IsNullOrEmpty(datamodel) && string.Equals(datamodel.ToLower(), "paint_defect"))
            {
                Console.WriteLine($"Generating {datamodel} datamodel with args: {args["id"]}, {args["type"]}");
                properties["type"] = args["type"];
                properties["id"] = args["id"];
                var paintDataModel = new PaintDataModel(gatewayId, deviceId, properties);

                return paintDataModel;
            }
            if (!string.IsNullOrEmpty(datamodel) && string.Equals(datamodel.ToLower(), "location_sensor"))
            {
                Console.WriteLine($"Generating {datamodel} datamodel with args: {args["id"]}");
                var paintDataModel = new LocationSensorModel(gatewayId, deviceId);

                return paintDataModel;
            }

            return null;
        }

    }

}