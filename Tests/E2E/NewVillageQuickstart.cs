using RimWorks.Quickstarts;
using RimWorld;
using Verse;
namespace AncientMedievalJapanScenarios.E2E
{
    // Select the production Scenario; do not replace its pawn/items/research parts.
    public sealed class AmjScenarioVillageQuickstart : AbstractQuickstart
    {
        public override TaggedString description
        {
            get { return "Starts the production AMJC New Village scenario for Pickle verification."; }
        }

        public override ScenarioDef scenario
        {
            get { return DefDatabase<ScenarioDef>.GetNamed("AMJC_NewVillage"); }
        }

        public override int mapSize
        {
            get { return 75; }
        }

        public override string seed
        {
            get { return "AMJ-New-Village-E2E"; }
        }
    }
}
