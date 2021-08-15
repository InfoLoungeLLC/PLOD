import random

def select_samples(levels, samples):
    if levels['close_contact'] == "HighLevelCloseContact":
        # 0の時の条件が上手く検出されない
        use_condition = random.randint(0, 2)
        
        if use_condition == 0:
            # 1の条件のみを満たす
            filter_samples = list(filter(lambda place: place['droplet_reachable_activity'] > 1, samples['place']))
            droplet_reachable_count = random.randint(0, 1)

        elif use_condition == 1:
            # 2の条件のみを満たす
            filter_samples = list(filter(lambda place: place['droplet_reachable_activity'] < 2, samples['place']))
            droplet_reachable_count = random.randint(2, 3)

        else:
            # 両方の条件を満たす
            filter_samples = list(filter(lambda place: place['droplet_reachable_activity'] > 1, samples['place']))
            droplet_reachable_count = random.randint(2, 3)

    elif levels['close_contact'] == "MediumLevelCloseContact":
        # 0の時の条件が上手く検出されない
        use_condition = random.randint(0, 2)
        
        if use_condition == 0:
            # 1の条件のみを満たす
            filter_samples = list(filter(lambda place: place['droplet_reachable_activity'] == 1, samples['place']))
            droplet_reachable_count = 0

        elif use_condition == 1:
            # 2の条件のみを満たす
            filter_samples = list(filter(lambda place: place['droplet_reachable_activity'] == 0, samples['place']))
            droplet_reachable_count = 1

        else:
            # 両方の条件を満たす
            filter_samples = list(filter(lambda place: place['droplet_reachable_activity'] == 1, samples['place']))
            droplet_reachable_count = 1

    else:
        # LowLevelCloseContactのとき
        filter_samples = list(filter(lambda place: place['droplet_reachable_activity'] == 0, samples['place']))
        droplet_reachable_count = 0

    
    not_droplet_reachable_count = random.randint(0, 3 - droplet_reachable_count)
    location = random.choice(filter_samples)
    droplet_reachable_actions = random.sample(samples['reachable_activity'], droplet_reachable_count)
    not_droplet_reachable_actions = random.sample(samples['not_reachable_activity'], not_droplet_reachable_count)
    actions = droplet_reachable_actions + not_droplet_reachable_actions
    return location, actions


def activity_situation(levels, risk_activity_situation_samples):
    if levels['close_contact'] == "HighLevelCloseContact" or levels['close_contact'] == "MediumLevelCloseContact" or levels['crowding'] == "HighLevelCrowding" or levels['crowding'] == "MediumLevelCrowding":
        risk_activity_situation_count = random.randint(1, 2)
    else:
        risk_activity_situation_count = 0

    risk_activity_situations = random.sample(risk_activity_situation_samples, risk_activity_situation_count)
    return risk_activity_situation_count, risk_activity_situations

def random_duration(levels):
    if levels['close_contact'] == "HighLevelCloseContact" or levels['close_contact'] == "MediumLevelCloseContact" :
        return random.randint(16, 30)
    else:
        return random.randint(0, 15)

def space_situation(levels, risk_spaces_situation_samples):
    if levels['crowding'] == "HighLevelCrowding":
        # 中身が2種類しかないのでそのまま返す
        return risk_spaces_situation_samples

    elif levels['crowding'] == "MediumLevelCrowding":
        risk_spaces_situations = random.choice(risk_spaces_situation_samples)
        return [risk_spaces_situations]

    elif levels['closed_space'] == "HighLevelClosedSpace":
        risk_spaces_situations = random.choice(risk_spaces_situation_samples)
        return [risk_spaces_situations]

def situation_type(levels, situation_samples):
    situation = None
    if levels['closed_space'] == "HighLevelClosedSpace" or levels['closed_space'] == "MediumLevelClosedSpace":
        situation = random.choice(situation_samples)
    return situation

        
