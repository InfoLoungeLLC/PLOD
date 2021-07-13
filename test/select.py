import random

def activity(close_contact_level, place_samples, reachable_activity_samples, not_reachable_activity_samples):
    if close_contact_level == "HighLevelCloseContact":
        # 0の時の条件が上手く検出されない
        use_condition = random.randint(0, 2)
        
        if use_condition == 0:
            # 1の条件のみを満たす
            filter_samples = list(filter(lambda place: place['DropletReachableActivity'] > 1, place_samples))
            droplet_reachable_count = random.randint(0, 1)

        elif use_condition == 1:
            # 2の条件のみを満たす
            filter_samples = list(filter(lambda place: place['DropletReachableActivity'] < 2, place_samples))
            droplet_reachable_count = random.randint(2, 3)

        else:
            # 両方の条件を満たす
            filter_samples = list(filter(lambda place: place['DropletReachableActivity'] > 1, place_samples))
            droplet_reachable_count = random.randint(2, 3)

    elif close_contact_level == "MiddleLevelCloseContact":
        # 0の時の条件が上手く検出されない
        use_condition = random.randint(0, 2)
        
        if use_condition == 0:
            # 1の条件のみを満たす
            filter_samples = list(filter(lambda place: place['DropletReachableActivity'] == 1, place_samples))
            droplet_reachable_count = 0

        elif use_condition == 1:
            # 2の条件のみを満たす
            filter_samples = list(filter(lambda place: place['DropletReachableActivity'] == 0, place_samples))
            droplet_reachable_count = 1

        else:
            # 両方の条件を満たす
            filter_samples = list(filter(lambda place: place['DropletReachableActivity'] == 1, place_samples))
            droplet_reachable_count = 1

    else:
        # LowLevelCloseContactのとき
        filter_samples = list(filter(lambda place: place['DropletReachableActivity'] == 0, place_samples))      
        droplet_reachable_count = 0

    
    not_droplet_reachable_count = random.randint(0, 3 - droplet_reachable_count)
    location = random.choice(filter_samples)
    droplet_reachable_actions = random.sample(reachable_activity_samples, droplet_reachable_count)
    not_droplet_reachable_actions = random.sample(not_reachable_activity_samples, not_droplet_reachable_count)
    actions = droplet_reachable_actions + not_droplet_reachable_actions
    return location, actions


def activity_situation(close_contact_level, risk_activity_situation_samples):
    if close_contact_level == "HighLevelCloseContact" or close_contact_level == "MiddleLevelCloseContact":
        risk_activity_situation_count = random.randint(1, 2)

    else:
        risk_activity_situation_count = 0

    risk_activity_situations = random.sample(risk_activity_situation_samples, risk_activity_situation_count)
    return risk_activity_situation_count, risk_activity_situations

def random_duration(close_contact_level):
    if close_contact_level == "HighLevelCloseContact" or close_contact_level == "MiddleLevelCloseContact" :
        return random.randint(16, 30)
    else:
        return random.randint(0, 15)

def space_situation(crowding_level, risk_spaces_situation_samples):
    if crowding_level == "HighLevelClosedSpace":
        # 中身が2種類しかないのでそのまま返す
        return risk_spaces_situation_samples

    elif crowding_level == "MiddleLevelClosedSpace":
        risk_spaces_situations = random.choice(risk_spaces_situation_samples)
        return risk_spaces_situations

