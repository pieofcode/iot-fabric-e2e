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
    public abstract class MESBaseEvent
    {
        public string GatewayId { get; internal set; }
        public string DeviceId { get; internal set; }
        public DateTime EventDate { get; set; }

        public string AssemblyLine { get; set; }

        public string Part { get; set; }

        public int Shift { get; set; }

    }

    public class PaintEvent : MESBaseEvent
    {
        public string DefectCode { get; set; }
        public string OccurrencePhase { get; set; }

    }

    public static class ModelInitializer
    {
        static string[] s_defectCodes = new string[]
        {
            "PD0", "PD1", "PD2", "PD3", "PD5", "PD7", "PD8", "PD9",
            "PD10", "PD11", "PD12", "PD14", "PD15", "PD16", "PD22",
        };

        static string[] s_defectCodesA = new string[]
        {
            "CC", "BD", "BI", "BO", "CR", "DU", "CO", "IT",
            "PG", "OP", "LI", "SC", "CH", "WS", "OH",
        };

        static string[] s_defectCodesB = new string[]
        {
            "0", "1", "2", "3", "4", "5", "6", "7", "8", "9",
            "10", "11", "12", "13"
        };

        static string[] s_defectCodesC = new string[]
        {
            "FCGD", "VFLB", "ZQRD", "FMPM", "CPYV", "KXDB", "PWOI", "SYPD","EJYN"
        };

        private static Random rng = new Random();

        public static void Shuffle<T>(this IList<T> list)
        {
            int n = list.Count;
            while (n > 1)
            {
                n--;
                int k = rng.Next(n + 1);
                T value = list[k];
                list[k] = list[n];
                list[n] = value;
            }
        }

        public static List<string> RandomizeList(List<string> values, string filler = "", int count = 0)
        {
            if (count > 0)
            {
                for (int i = 0; i < count; i++)
                {
                    values.Add(filler);
                }
            }

            values.Shuffle<string>();
            return values;
        }

        public static string[] GetDefectCodes(string type)
        {
            List<string> codes = null;

            if (string.Equals(type.ToUpper(), "A"))
            {
                codes = ModelInitializer.RandomizeList(s_defectCodesA.ToList(), "", 20);
            }
            if (string.Equals(type.ToUpper(), "B"))
            {
                codes = ModelInitializer.RandomizeList(s_defectCodesB.ToList(), "", 20);
            }
            if (string.Equals(type.ToUpper(), "C"))
            {
                codes = ModelInitializer.RandomizeList(s_defectCodesC.ToList(), "", 20);
            }

            if (codes != null)
            {
                return codes.ToArray();
            }

            return null;
        }

        public static string[] GetOccurrancePhases()
        {
            var occurrencePhases = new string[] { "POST_MOLD", "PRE_PAINT", "POST_PAINT", "POST_ASSEMBLY" };
            return occurrencePhases;
        }

        public static string[] GetParts()
        {
            var parts = new string[] { "MXP-AX-0830", "MXP-BY-0380", "MXP-CZ-9800" };
            return parts;
        }
    }

    public class OperationAlert
    {
        public string AssemblyLine { get; set; }
        public double Temperature { get; set; }
        public DateTime EventDate { get; set; }
    }

    public class PaintDataModel : BaseDataModel
    {

        public string Type
        {
            get
            {
                return this.Properties["type"];
            }
        }

        public PaintDataModel(string gatewayId, string deviceId, Dictionary<string, string> properties = null) : base(gatewayId, deviceId, properties)
        {

        }

        public override IList<string> GenerateTelemetry()
        {
            var strMessages = new List<string>();

            DateTime ts = DateTime.UtcNow;
            var paintEventDataFaker = new Faker<PaintEvent>()
                    .RuleFor(x => x.GatewayId, this.GatewayId)
                    .RuleFor(x => x.DeviceId, this.DeviceId)
                    .RuleFor(x => x.AssemblyLine, this.Type.ToUpper())
                    .RuleFor(x => x.DefectCode, f => f.PickRandom(ModelInitializer.GetDefectCodes(this.Type)))
                    .RuleFor(x => x.OccurrencePhase, f => f.PickRandom(ModelInitializer.GetOccurrancePhases()))
                    .RuleFor(x => x.Part, f => f.PickRandom(ModelInitializer.GetParts()))
                    .RuleFor(x => x.EventDate, ts)
                    .RuleFor(x => x.Shift, (Math.Abs(ts.Minute / 480) + 1));

            var paintEvent = paintEventDataFaker.Generate();
            if (string.IsNullOrEmpty(paintEvent.DefectCode))
            {
                paintEvent.OccurrencePhase = null;
            }
            string messageBody = JsonSerializer.Serialize(paintEvent);
            strMessages.Add(messageBody);

            return strMessages;
        }

    }


}