def experience_weight(years):
    """
    Non-linear experience weighting that rewards growth but caps diminishing returns.
    0-2 years: building foundation (ascending)
    2-5 years: solid expertise (strong)
    5-10 years: proven expert (very strong, slight diminishing returns)
    10+ years: expert+ (caps at high value, doesn't dominate over skills)
    
    Unlike linear scaling, this prevents 11 years from being treated 2.2x better than 5 years.
    """
    if years >= 10:
        return 0.95  
    elif years >= 7:
        return 0.88
    elif years >= 5:
        return 0.80
    elif years >= 3:
        return 0.65
    elif years >= 2:
        return 0.55
    else:
        return 0.40


def calculate_balance_score(skills, experience_weight_val, semantic):
    """
    Calculate a balance factor that rewards consistency and interdependence.
    Penalizes extreme imbalance (e.g., 80% skills but 40% semantic).
    
    Uses coefficient of variation approach:
    - Candidates with balanced scores get a multiplier
    - Candidates with lopsided scores get slightly penalized
    
    Range: 0.7 to 1.0 (70% to 100%)
    """
    scores = [skills, experience_weight_val, semantic]
    mean_score = sum(scores) / len(scores)
    
    if mean_score == 0:
        return 0.7
    
    # Calculate variance
    variance = sum((x - mean_score) ** 2 for x in scores) / len(scores)
    std_dev = variance ** 0.5
    coeff_variation = std_dev / mean_score if mean_score > 0 else 0
    
    # Convert CVar to balance bonus
    # CV=0 (perfect balance) -> 1.0 multiplier
    # CV>0.5 (imbalanced) -> 0.75 multiplier
    balance_bonus = max(0.7, 1.0 - (coeff_variation * 0.3))
    
    return balance_bonus


def calculate_score(similarity, years, skill_score):
    """
    Intelligent relative scoring that considers all dimensions holistically.
    
    Core principles:
    1. Skills (0.40): Most important - direct job fit evaluation
    2. Semantic (0.30): Important - shows role understanding
    3. Experience (0.30): Important - validates capability (not dominant)
    
    Enhancement: Balance factor rewards well-rounded candidates, penalizes extremes.
    
    Why this is smarter:
    - A candidate with (75% skills, 75% semantic, 3 yrs exp) scores higher than 
      (58% skills, 59% semantic, 5 yrs exp) because demonstrated fit matters more
    - Experience serves as validation, not override
    - Consistency is rewarded - you can't be weak in skills but strong overall
    """
    # Get experience weight (caps at 0.95 to prevent dominance)
    exp_weight = experience_weight(years)
    
    # Base score with rebalanced weights
    base_score = (skill_score * 0.40) + (similarity * 0.30) + (exp_weight * 0.30)
    
    # Calculate balance factor (1.0 = perfect balance, 0.7 = highly imbalanced)
    balance = calculate_balance_score(skill_score, exp_weight, similarity)
    
    # Apply balance factor - rewards interdependence between dimensions
    final_score = base_score * balance
    
    return final_score