import random

def activity(close_contact_level, place_samples, activity_samples):
    if close_contact_level == "HighLevelCloseContact":
        # 0の時の条件が上手く検出されない
        use_condition = random.randint(0, 2)
        
        droplet_reachable = list()
        not_droplet_reachable = list()

        # DropletReachableか否かで分類する
        for action in activity_samples:
            if action["isDropletReachableActivity"]:
                droplet_reachable.append(action)
            else:
                not_droplet_reachable.append(action)
        
        if use_condition == 0:
            # 1の条件のみを満たす
            filter_samples = list(filter(lambda place: place['DropletReachableActivity'] > 1, place_samples))

            droplet_reachable_count = random.randint(0, 1)
            not_droplet_reachable_count = random.randint(0, 3 - droplet_reachable_count)


        elif use_condition == 1:
            # 2の条件のみを満たす
            filter_samples = list(filter(lambda place: place['DropletReachableActivity'] < 2, place_samples))

            droplet_reachable_count = random.randint(2, 3)
            not_droplet_reachable_count = random.randint(0, 3 - droplet_reachable_count)

        else:
            # 両方の条件を満たす
            filter_samples = list(filter(lambda place: place['DropletReachableActivity'] > 1, place_samples))

            droplet_reachable_count = random.randint(2, 3)
            not_droplet_reachable_count = random.randint(0, 3 - droplet_reachable_count)

        location = random.choice(filter_samples)
        droplet_reachable_actions = random.sample(droplet_reachable, droplet_reachable_count)
        not_droplet_reachable_actions = random.sample(not_droplet_reachable, not_droplet_reachable_count)
        actions = droplet_reachable_actions + not_droplet_reachable_actions
        return location, actions


def activity_situation(close_contact_level, risk_activity_situation_samples):
    if close_contact_level == "HighLevelCloseContact" or close_contact_level == "MiddleLevelCloseContact":
        risk_activity_situation_count = random.randint(1, 2)
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

