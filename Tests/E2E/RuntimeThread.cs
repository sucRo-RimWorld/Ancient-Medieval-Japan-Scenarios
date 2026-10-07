using System;
using System.Threading.Tasks;
using Verse;
namespace AncientMedievalJapanScenarios.E2E
{
    // Pickle can resume its scenario pipeline on a worker thread. Unity textures
    // and live Verse map collections must always be accessed in the driver Update.
    internal static class RuntimeThread
    {
        public static Task Run(Action assertion)
        {
            var completion = new TaskCompletionSource<bool>();
            RimWorks.Pickle.Runtime.PickleDriver.Post(delegate
            {
                try
                {
                    if (!UnityData.IsInMainThread)
                        throw new InvalidOperationException("AMJ runtime assertion must run on the Unity main thread.");
                    assertion();
                    completion.SetResult(true);
                }
                catch (Exception error) { completion.SetException(error); }
            });
            return completion.Task;
        }
    }

}
