from unittest.mock import Mock
from analytics.application.use_cases.compute_centrality import ComputeCentralityUseCase
from analytics.application.use_cases.detect_communities import DetectCommunitiesUseCase
from analytics.application.use_cases.find_shortest_path import FindShortestPathUseCase
from analytics.domain.entities import CentralityType, CentralityScore, Community, PathResult
from shared_kernel.domain.value_objects import EntityId

def test_compute_centrality_use_case():
    mock_port = Mock()
    mock_port.compute_centrality.return_value = [
        CentralityScore(entity_id=EntityId("e1"), score=0.9),
        CentralityScore(entity_id=EntityId("e2"), score=0.1)
    ]
    
    use_case = ComputeCentralityUseCase(mock_port)
    results = use_case.execute(CentralityType.DEGREE)
    
    assert len(results) == 2
    assert results[0].entity_id.value == "e1"
    assert results[0].score == 0.9
    mock_port.compute_centrality.assert_called_once_with(CentralityType.DEGREE)

def test_detect_communities_use_case():
    mock_port = Mock()
    mock_port.detect_communities.return_value = [
        Community(community_id=0, member_entity_ids=[EntityId("e1"), EntityId("e2")]),
        Community(community_id=1, member_entity_ids=[EntityId("e3")])
    ]
    
    use_case = DetectCommunitiesUseCase(mock_port)
    results = use_case.execute()
    
    assert len(results) == 2
    assert len(results[0].member_entity_ids) == 2
    mock_port.detect_communities.assert_called_once()

def test_find_shortest_path_use_case():
    mock_port = Mock()
    mock_port.shortest_path.return_value = PathResult(found=True, entity_ids=[EntityId("e1"), EntityId("e2")])
    
    use_case = FindShortestPathUseCase(mock_port)
    result = use_case.execute(EntityId("e1"), EntityId("e2"))
    
    assert result.found is True
    assert len(result.entity_ids) == 2
    mock_port.shortest_path.assert_called_once_with(EntityId("e1"), EntityId("e2"))
