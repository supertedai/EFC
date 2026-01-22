"""
Example: Regime Detection in Validity-Aware AI

This example demonstrates basic usage of the EBE filter for
regime-aware inference.

Part of: Validity-Aware AI
DOI: 10.6084/m9.figshare.31122970
"""

# Note: This example uses mock data. In production, connect to real
# Neo4j and Qdrant instances.


def example_basic_classification():
    """
    Example 1: Basic regime classification from entropy value.
    """
    from src.regime_classifier import classify_regime, Regime
    
    print("=" * 60)
    print("Example 1: Basic Regime Classification")
    print("=" * 60)
    
    # Test different entropy values
    test_cases = [
        (0.15, "Low entropy - should be L1"),
        (0.45, "Medium entropy - should be L2"),
        (0.85, "High entropy - should be L3"),
    ]
    
    for entropy, description in test_cases:
        regime, confidence = classify_regime(entropy)
        print(f"\nEntropy: {entropy:.2f} ({description})")
        print(f"  Regime: {regime.name}")
        print(f"  Confidence: {confidence:.2f}")
        print(f"  Allows confident output: {regime.allows_confident_output}")


def example_entropy_computation():
    """
    Example 2: Computing entropy from graph and retrieval data.
    """
    from src.entropy_measures import compute_total_entropy
    
    print("\n" + "=" * 60)
    print("Example 2: Entropy Computation")
    print("=" * 60)
    
    # Mock subgraph data
    mock_subgraph = {
        "nodes": [
            {"id": "1", "name": "Climate Change", "confidence": 0.9},
            {"id": "2", "name": "Temperature Rise", "confidence": 0.85},
            {"id": "3", "name": "Sea Level", "confidence": 0.8, "conflicts": ["measurement_dispute"]},
        ],
        "edges": [
            {"type": "CAUSES", "confidence": 0.9},
            {"type": "CORRELATES", "confidence": 0.7},
            {"type": "DISPUTED_BY", "confidence": 0.5},
        ]
    }
    
    # Mock retrieved chunks
    mock_chunks = [
        {"source": "ipcc_report", "confidence": 0.95},
        {"source": "research_paper_1", "confidence": 0.8},
        {"source": "news_article", "confidence": 0.6},
        {"source": "blog_post", "confidence": 0.4, "contradiction_flag": True},
    ]
    
    # Compute entropy
    result = compute_total_entropy(mock_subgraph, mock_chunks)
    
    print(f"\nTotal Entropy: {result['total']:.3f}")
    print("\nComponent Breakdown:")
    for component, value in result['components'].items():
        print(f"  {component}: {value:.3f}")


def example_protocol_selection():
    """
    Example 3: Selecting response protocols based on regime.
    """
    from src.regime_classifier import Regime
    from src.response_protocols import get_protocol, ProtocolEngine
    
    print("\n" + "=" * 60)
    print("Example 3: Response Protocol Selection")
    print("=" * 60)
    
    engine = ProtocolEngine()
    
    for regime in [Regime.L1, Regime.L2, Regime.L3]:
        protocol = engine.get_protocol(regime)
        print(f"\nRegime: {regime.name}")
        print(f"  Protocol: {protocol.name}")
        print(f"  User Indicator: {protocol.user_indicator}")
        print(f"  Point estimates allowed: {protocol.constraints['point_estimates']}")
        print(f"  Confidence ceiling: {protocol.constraints['confidence_ceiling']}")


def example_full_pipeline():
    """
    Example 4: Full pipeline simulation (without real database connections).
    """
    from src.regime_classifier import RegimeClassifier
    from src.entropy_measures import compute_total_entropy
    from src.response_protocols import ProtocolEngine
    
    print("\n" + "=" * 60)
    print("Example 4: Full Pipeline Simulation")
    print("=" * 60)
    
    # Initialize components
    classifier = RegimeClassifier(theta_L1=0.3, theta_L2=0.7)
    engine = ProtocolEngine()
    
    # Simulate a query about a contested topic
    print("\nSimulating query: 'What are the effects of social media on mental health?'")
    
    # Mock data for contested topic
    mock_subgraph = {
        "nodes": [
            {"id": "1", "name": "Social Media", "confidence": 0.95},
            {"id": "2", "name": "Mental Health", "confidence": 0.9},
            {"id": "3", "name": "Depression", "confidence": 0.8, 
             "definitions": ["clinical definition", "colloquial use"]},
            {"id": "4", "name": "Anxiety", "confidence": 0.75},
        ],
        "edges": [
            {"type": "MAY_CAUSE", "confidence": 0.6},
            {"type": "CORRELATES", "confidence": 0.7},
            {"type": "DISPUTED", "confidence": 0.4},
            {"type": "SUPPORTS", "confidence": 0.5},
        ]
    }
    
    mock_chunks = [
        {"source": "study_2023", "confidence": 0.8},
        {"source": "study_2022", "confidence": 0.75, "contradiction_flag": True},
        {"source": "meta_analysis", "confidence": 0.85},
        {"source": "opinion_piece", "confidence": 0.3},
    ]
    
    # Step 1: Compute entropy
    entropy_result = compute_total_entropy(mock_subgraph, mock_chunks)
    print(f"\n1. Computed entropy: {entropy_result['total']:.3f}")
    
    # Step 2: Classify regime
    regime, confidence = classifier.classify(entropy_result['total'])
    print(f"2. Classified regime: {regime.name} (confidence: {confidence:.2f})")
    
    # Step 3: Get protocol
    protocol = engine.get_protocol(regime)
    print(f"3. Selected protocol: {protocol.name}")
    
    # Step 4: Show constraints
    print("\n4. Generation Constraints:")
    for key, value in protocol.constraints.items():
        print(f"   {key}: {value}")
    
    # Step 5: Show system prompt addition
    print("\n5. System Prompt Addition:")
    if protocol.system_prompt_addition:
        # Show first 200 chars
        preview = protocol.system_prompt_addition[:200]
        print(f"   {preview}...")
    else:
        print("   (none - standard generation)")
    
    # Step 6: User indicator
    print(f"\n6. User would see: {protocol.user_indicator}")


def example_validation():
    """
    Example 5: Validating responses against protocol constraints.
    """
    from src.regime_classifier import Regime
    from src.response_protocols import ProtocolEngine
    
    print("\n" + "=" * 60)
    print("Example 5: Response Validation")
    print("=" * 60)
    
    engine = ProtocolEngine()
    
    # Get L2 protocol (requires citations and uncertainty)
    protocol = engine.get_protocol(Regime.L2)
    
    # Test responses
    responses = [
        ("The effect is exactly 45% increase in anxiety.", "Missing hedging and citations"),
        ("Studies suggest approximately 30-50% correlation [1].", "Proper hedging and citation"),
        ("According to Smith et al., there may be a link.", "Has citation and hedging"),
    ]
    
    print(f"\nValidating against protocol: {protocol.name}")
    
    for response, description in responses:
        result = engine.validate_response(response, protocol)
        print(f"\nResponse: '{response[:50]}...'")
        print(f"  Description: {description}")
        print(f"  Valid: {result['valid']}")
        if result['violations']:
            print(f"  Violations: {result['violations']}")
        if result['warnings']:
            print(f"  Warnings: {result['warnings']}")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("VALIDITY-AWARE AI - EXAMPLES")
    print("DOI: 10.6084/m9.figshare.31122970")
    print("=" * 60)
    
    example_basic_classification()
    example_entropy_computation()
    example_protocol_selection()
    example_full_pipeline()
    example_validation()
    
    print("\n" + "=" * 60)
    print("Examples complete.")
    print("=" * 60)
