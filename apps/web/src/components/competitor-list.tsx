import type { CompetitorStore } from "@/lib/types";

import { NearbyCompetitorList } from "./nearby-competitor-list";

type CompetitorListProps = {
  stores: CompetitorStore[];
};

export function CompetitorList({ stores }: CompetitorListProps) {
  return <NearbyCompetitorList stores={stores} />;
}
