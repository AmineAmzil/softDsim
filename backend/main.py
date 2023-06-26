import boto3
from io import StringIO
from userparameter.set1 import USERPARAMETERS
from simulation_framework.wrappers import FastSecenario, FastTasks
from app.dto.request import SimulationRequest, Workpack
from app.src.simulation import simulate
from app.models.user_scenario import ScenarioState, UserScenario
from app.models.team import Member, SkillType, Team
from app.models.task import Task
from app.models.scenario import ScenarioConfig
from pandas import DataFrame
import numpy as np
from typing import List
from statistics import mean
import random
from random import randint
import os
from dotenv import load_dotenv
import json


print("MAIN SCRIPT")

skill_type_ids: List[int] = []


def check_file_exists(file_path):
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"The file '{file_path}' does not exist.")


def check_skilltype_ids(text: str) -> bool:
    text = text.strip()

    if text == "":
        return False

    try:
        return len([int(x.strip()) for x in text.split(',')]) == 3
    except:
        return False


def validate_settings_file(file_path):
    required_attributes = ["bucket", "USE_S3", "DATAPATH", "RUNNAME", "NRUNS", "SAVE_EVERY", "NUMBER_OF_SK_PER_TEAM",
                           "SKILL_TYPE_IDS", "IS_RANDOM_HYPERPARAMS", "IS_RANDOM_USERPARAMS", "IS_RANDOM_SKILL_TYPE_IDS", "IS_RANDOM_SKILL_TYPE"]
    load_dotenv(file_path)

    missing_attributes = [
        attr for attr in required_attributes if os.getenv(attr) is None]

    if missing_attributes:
        raise ValueError(
            f"Missing attributes in the .env file: {', '.join(missing_attributes)}")

    if int(os.getenv("NUMBER_OF_SK_PER_TEAM")) < 1 or int(os.getenv("NUMBER_OF_SK_PER_TEAM")) > 10:
        raise ValueError(
            f"Unvalid value of attribute 'NUMBER_OF_SK_PER_TEAM' in the settings.env file. NUMBER_OF_SK_PER_TEAM should be > 0 and <= 10")

    if not check_skilltype_ids(os.getenv("SKILL_TYPE_IDS")):
        raise ValueError(
            f"Unvalid value of attribute 'SKILL_TYPE_IDS' in the settings.env file. SKILL_TYPE_IDS should like '1,2,3' len = 3.")

    if str(os.getenv("IS_RANDOM_HYPERPARAMS")).lower().strip() not in ["true", "false"]:
        raise ValueError(
            f"Unvalid value of attribute 'IS_RANDOM_HYPERPARAMS' in the settings.env file. IS_RANDOM_HYPERPARAMS should be False or True.")

    if str(os.getenv("IS_RANDOM_USERPARAMS")).lower().strip() not in ["true", "false"]:
        raise ValueError(
            f"Unvalid value of attribute 'IS_RANDOM_USERPARAMS' in the settings.env file. IS_RANDOM_USERPARAMS should be False or True.")

    if str(os.getenv("IS_RANDOM_SKILL_TYPE_IDS")).lower().strip() not in ["true", "false"]:
        raise ValueError(
            f"Unvalid value of attribute 'IS_RANDOM_SKILL_TYPE_IDS' in the settings.env file. IS_RANDOM_SKILL_TYPE_IDS should be False or True.")

    if str(os.getenv("IS_RANDOM_SKILL_TYPE")).lower().strip() not in ["true", "false"]:
        raise ValueError(
            f"Unvalid value of attribute IS_RANDOM_SKILL_TYPE in the settings.env file. IS_RANDOM_SKILL_TYPE should be False or True.")


load_dotenv("settings.env")

bucket = os.getenv("bucket")
USE_S3 = os.getenv("USE_S3", 'False').lower() in ('true', '1', 't')
DATAPATH = os.getenv("DATAPATH")
RUNNAME = os.getenv("RUNNAME")
NRUNS = int(os.getenv("NRUNS"))
SAVE_EVERY = int(os.getenv("SAVE_EVERY"))
NUMBER_OF_SK_PER_TEAM = int(os.getenv("NUMBER_OF_SK_PER_TEAM"))

IS_RANDOM_HYPERPARAMS = os.getenv(
    "IS_RANDOM_HYPERPARAMS", 'False').lower().strip() in ('true', 't')
IS_RANDOM_USERPARAMS = os.getenv(
    "IS_RANDOM_USERPARAMS", 'False').lower().strip() in ('true', 't')
IS_RANDOM_SKILL_TYPE_IDS = os.getenv(
    "IS_RANDOM_SKILL_TYPE_IDS", 'False').lower().strip() in ('true', 't')
IS_RANDOM_SKILL_TYPE = os.getenv(
    "IS_RANDOM_SKILL_TYPE", 'False').lower().strip() in ('true', 't')
SKILL_TYPE_IDS: List[int] = [int(x.strip())
                             for x in os.getenv("SKILL_TYPE_IDS").split(',')]

Team.objects.create()


def validate_skill_type_data(skill_type_data):
    required_attributes = ['name', 'cost_per_day', 'error_rate', 'throughput', 'management_quality',
                           'development_quality', 'signing_bonus']
    for attribute in required_attributes:
        if attribute not in skill_type_data:
            raise ValueError(
                f"Missing attribute '{attribute}' in skill type data.")

        value = skill_type_data[attribute]

        if attribute == 'name' and not isinstance(value, str):
            raise ValueError(
                f"Invalid value for attribute 'name'. It should be a string.")

        if attribute == 'cost_per_day' and value <= 0:
            raise ValueError(
                "Invalid value for attribute 'cost_per_day'. It should be greater than 0.")

        if attribute == 'error_rate' and (value < 0 or value > 1):
            raise ValueError(
                f"Invalid value for attribute 'error_rate'. It should be a value between 0 and 1.")

        if attribute in ['throughput', 'management_quality', 'development_quality']:
            if value < 0:
                raise ValueError(
                    f"Invalid value for attribute '{attribute}'. It should be greater than or equal to 0.")

        if attribute == 'signing_bonus' and value < 0:
            raise ValueError(
                "Invalid value for attribute 'signing_bonus'. It should be greater than or equal to 0.")


def validate_scenario_config_data(data):
    required_attributes = ['name', 'stress_weekend_reduction', 'stress_overtime_increase', 'stress_error_increase',
                           'done_tasks_per_meeting', 'train_skill_increase_rate']
    for attribute in required_attributes:
        if attribute not in data:
            raise ValueError(
                f"Missing attribute '{attribute}' in scenario config data.")

        value = data[attribute]

        if attribute == 'stress_weekend_reduction' and value >= 0:
            raise ValueError(
                "Invalid value for attribute 'stress_weekend_reduction'. It should be negative.")

        if attribute in ['stress_overtime_increase', 'stress_error_increase',
                         'done_tasks_per_meeting', 'train_skill_increase_rate']:
            if (value < 0 or value > 100):
                raise ValueError(
                    f"Invalid value for attribute '{attribute}'. It should be between 0 and 100.")


def retrieve_skill_types_from_json() -> List[SkillType]:
    file_path = "skilltypes.json"
    check_file_exists(file_path)

    with open(file_path, 'r') as json_file:
        data = json.load(json_file)

    skill_types: List[SkillType] = []

    for skill_type_data in data:
        validate_skill_type_data(skill_type_data)
        sk: SkillType = SkillType.objects.create(
            name=skill_type_data['name'],
            cost_per_day=skill_type_data['cost_per_day'],
            error_rate=skill_type_data['error_rate'],
            throughput=skill_type_data['throughput'],
            management_quality=skill_type_data['management_quality'],
            development_quality=skill_type_data['development_quality'],
            signing_bonus=skill_type_data['signing_bonus']

        )
        skill_types.append(sk)

    return skill_types


def retrieve_scenario_config_from_json() -> ScenarioConfig:
    file_path = "scenario_config.json"
    check_file_exists(file_path)

    with open(file_path, 'r') as json_file:
        data = json.load(json_file)

    validate_scenario_config_data(data)

    name = data['name']
    stress_weekend_reduction = data['stress_weekend_reduction']
    stress_overtime_increase = data['stress_overtime_increase']
    stress_error_increase = data['stress_error_increase']
    done_tasks_per_meeting = data['done_tasks_per_meeting']
    train_skill_increase_rate = data['train_skill_increase_rate']
    cost_member_team_event = data["cost_member_team_event"]
    randomness = data["randomness"]

    scenario_config = ScenarioConfig(
        name=name,
        stress_weekend_reduction=stress_weekend_reduction,
        stress_overtime_increase=stress_overtime_increase,
        stress_error_increase=stress_error_increase,
        done_tasks_per_meeting=done_tasks_per_meeting,
        train_skill_increase_rate=train_skill_increase_rate,
    )

    scenario_config.cost_member_team_event = cost_member_team_event
    scenario_config.randomness = randomness

    return scenario_config


def init_scenario() -> UserScenario:
    us = UserScenario.objects.create()
    state = ScenarioState.objects.create(user_scenario=us)
    team = Team.objects.create(user_scenario=us)
    return us, state, team


def init_config():
    pass


def generate_random_skilltype() -> SkillType:
    sk: SkillType = SkillType.objects.create()

    sk.name = f"random_{randint(10000000,99999999)}"
    sk.throughput = randint(1, 5)
    sk.error_rate = round(random.random() * 0.23 + 0.1, 2)
    sk.cost_per_day = randint(100, 300)
    sk.development_quality = randint(5, 100)
    sk.management_quality = randint(5, 100)
    sk.signing_bonus = 999

    return sk


def init_skill_types() -> List[SkillType]:
    SkillType.objects.all().delete()

    if IS_RANDOM_SKILL_TYPE:
        print("RANDOM SKILL TYPES")
        return [generate_random_skilltype() for _ in range(3)]

    print("GIVEN SKILL TYPES")
    return retrieve_skill_types_from_json()


def init_members(skill_types: List[SkillType]) -> List[Member]:
    members: List[Member] = []

    # If the skill types are generated randomly, we are sure
    # the the list contains exactly 3 skill types
    # so we dont have to choose between them.
    if IS_RANDOM_SKILL_TYPE:
        for sk in skill_types:
            for _ in range(NUMBER_OF_SK_PER_TEAM):
                members.append(Member.objects.create(skill_type=sk, team_id=1))
        return members

    if IS_RANDOM_SKILL_TYPE_IDS:
        print("RANDOM SKILL TYPE IDS")
        [skill_type_ids.append(randint(0, len(skill_types) - 1))
         for _ in range(3)]

    else:
        print("GIVEN SKILL TYPE IDS")
        [skill_type_ids.append(x) for x in SKILL_TYPE_IDS]

        if len(skill_type_ids) > len(skill_types):
            raise ValueError(
                "Number of ids is bigger than the list of skilltypes.")

        for id in skill_type_ids:
            if id > len(skill_types) - 1:
                raise ValueError(f"Id {id} is out of bound.")

    for id in skill_type_ids:
        sk = skill_types[id]
        for _ in range(NUMBER_OF_SK_PER_TEAM):
            members.append(Member.objects.create(skill_type=sk, team_id=1))

    return members


def run_simulation(scenario, config, members, tasks, skill_types, rec, UP, UP_n):
    scenario.config = config
    s = FastSecenario(scenario, members, tasks, 1, 1)
    r = SimulationRequest(scenario_id=0, type="SIMULATION", actions=UP)
    simulate(r, s)
    rec.add(s, config, skill_types, UP, UP_n)


def generate_random_scneario_config() -> ScenarioConfig:
    ScenarioConfig.objects.all().delete()
    config: ScenarioConfig = ScenarioConfig.objects.create()

    config.id = 1
    config.name = f"random_config_{randint(10000000,99999999)}"
    config.stress_weekend_reduction = round(random.random() * 0.8, 2)
    config.stress_overtime_increase = round(random.random() * 0.25, 2)
    config.stress_error_increase = round(random.random() * 0.33, 2)
    config.done_tasks_per_meeting = randint(0, 5) * 20
    config.train_skill_increase_rate = round(random.random() * 0.5, 2)

    config.save()

    return config


def set_config() -> ScenarioConfig:
    if IS_RANDOM_HYPERPARAMS:
        print("RANDOM CONFIG")
        return generate_random_scneario_config()

    print("GIVEN CONFIG")
    return retrieve_scenario_config_from_json()


def set_tasks(u):
    TOTAL = 200
    tasks = set()
    for _ in range(int(TOTAL * 0.25)):
        tasks.add(Task(id=randint(0, 9999999999),
                  difficulty=1, user_scenario=u))
    for _ in range(int(TOTAL * 0.5)):
        tasks.add(Task(id=randint(0, 9999999999),
                  difficulty=2, user_scenario=u))
    for _ in range(int(TOTAL * 0.25)):
        tasks.add(Task(id=randint(0, 9999999999),
                  difficulty=3, user_scenario=u))
    return FastTasks(tasks)


def np_record(
    s: FastSecenario,
    config: ScenarioConfig,
    skill_types: List[SkillType],
    workpack: Workpack,
    UP_n,
) -> np.array:
    return np.array(
        [
            config.stress_weekend_reduction,
            config.stress_overtime_increase,
            config.stress_error_increase,
            config.done_tasks_per_meeting,
            config.train_skill_increase_rate,
            len(s.members),
            NUMBER_OF_SK_PER_TEAM,
            skill_types[skill_type_ids[0]].name,
            skill_types[skill_type_ids[0]].throughput,
            skill_types[skill_type_ids[0]].error_rate,
            skill_types[skill_type_ids[0]].cost_per_day,
            skill_types[skill_type_ids[0]].management_quality,
            skill_types[skill_type_ids[0]].development_quality,
            skill_types[skill_type_ids[0]].signing_bonus,
            skill_types[skill_type_ids[1]].name,
            skill_types[skill_type_ids[1]].throughput,
            skill_types[skill_type_ids[1]].error_rate,
            skill_types[skill_type_ids[1]].cost_per_day,
            skill_types[skill_type_ids[1]].management_quality,
            skill_types[skill_type_ids[1]].development_quality,
            skill_types[skill_type_ids[1]].signing_bonus,
            skill_types[skill_type_ids[2]].name,
            skill_types[skill_type_ids[2]].throughput,
            skill_types[skill_type_ids[2]].error_rate,
            skill_types[skill_type_ids[2]].cost_per_day,
            skill_types[skill_type_ids[2]].management_quality,
            skill_types[skill_type_ids[2]].development_quality,
            skill_types[skill_type_ids[2]].signing_bonus,
            UP_n,
            workpack.days,
            workpack.bugfix,
            workpack.unittest,
            workpack.integrationtest,
            workpack.meetings,
            workpack.training,
            workpack.teamevent,
            workpack.salary,
            workpack.overtime,
            s.scenario.state.cost,
            s.scenario.state.day,
            mean([m.efficiency for m in s.members]),
            mean([m.familiarity for m in s.members]),
            mean([m.stress for m in s.members]),
            mean([m.xp for m in s.members]),
            mean([m.motivation for m in s.members]),
            len(s.tasks.accepted()),
            len(s.tasks.rejected()),
            IS_RANDOM_HYPERPARAMS,
            IS_RANDOM_USERPARAMS,
            IS_RANDOM_SKILL_TYPE,
            IS_RANDOM_SKILL_TYPE_IDS
        ]
    )


class NpRecord:
    def __init__(self):
        self.data = None

    def add(self, s: FastSecenario, *args):
        if self.data is None:
            self.data = np.array([np_record(s, *args)])
        else:
            self.data = np.vstack((self.data, np.array([np_record(s, *args)])))

    def clear(self):
        self.data = None

    def df(self):
        return DataFrame(
            self.data,
            columns=[
                "c_swr",
                "c_soi",
                "c_sei",
                "c_dtm",
                "c_tsi",
                "s_team_size",
                "s_number_of_sk_per_team",
                "s_1name",
                "s_1throughput",
                "s_1error_rate",
                "s_1cost_per_day",
                "s_1management_quality",
                "s_1development_quality",
                "s_1signing_bonus",
                "s_2name",
                "s_2throughput",
                "s_2error_rate",
                "s_2cost_per_day",
                "s_2management_quality",
                "s_2development_quality",
                "s_2signing_bonus",
                "s_3name",
                "s_3throughput",
                "s_3error_rate",
                "s_3cost_per_day",
                "s_3management_quality",
                "s_3development_quality",
                "s_3signing_bonus",
                "UP",
                "days",
                "bugfix",
                "unittest",
                "integrationtest",
                "meetings",
                "training",
                "teamevent",
                "salary",
                "overtime",
                "Cost",
                "Day",
                "Eff",
                "Fam",
                "Str",
                "XP",
                "Mot",
                "Acc",
                "Rej",
                "IS_RANDOM_HYPERPARAMS",
                "IS_RANDOM_USERPARAMS",
                "IS_RANDOM_SKILL_TYPE",
                "IS_RANDOM_SKILL_TYPE_IDS"
            ],
        )


def set_members(members: List[Member]):
    for member in members:
        member.familiar_tasks = 0
        member.familiarity = 0
        member.motivation = 0.75
        member.stress = 0.15
        member.xp = 0


def set_scenario(scenario: UserScenario, state: ScenarioState):
    state.cost = 0
    state.day = 0


def random_boolean() -> bool:
    return bool(random.getrandbits(1))


def random_number(start: int, end: int) -> int:
    if (start > end):
        tmp = end
        end = start
        start = tmp

    return randint(start, end)


def generate_user_params() -> Workpack:
    wp: Workpack = Workpack()

    wp.bugfix = random_boolean()
    wp.teamevent = random_boolean()
    wp.integrationtest = random_boolean()
    wp.unittest = random_boolean()
    wp.meetings = random_number(0, 5)
    wp.training = random_number(0, 3)
    wp.salary = random_number(0, 2)
    wp.overtime = random_number(-1, 2)

    return wp


def set_user_params() -> List[Workpack]:
    if IS_RANDOM_USERPARAMS:
        print("RANDOM USER PARAMS")
        return [generate_user_params() for _ in range(8)]

    print("GIVEN USER PARAMS")
    return USERPARAMETERS


def main():
    check_file_exists("settings.env")
    validate_settings_file("settings.env")
    print("Started")
    rec = NpRecord()
    scenario, state, team = init_scenario()
    skill_types = init_skill_types()
    members = init_members(skill_types)

    for x in range(1, NRUNS + 1):
        config: ScenarioConfig = set_config()
        user_params: List = set_user_params()

        for n, UP in enumerate(user_params):
            set_scenario(scenario, state)
            set_members(members)
            tasks = set_tasks(scenario)
            run_simulation(scenario, config, members,
                           tasks, skill_types, rec, UP, n)
            # print(f"{len(tasks.done())} \t {mean([m.efficiency for m in members])}")

        if x % SAVE_EVERY == 0:
            print(f"{x} of {NRUNS}")
            if USE_S3:
                print("Saving in S3")
                csv_buffer = StringIO()
                rec.df().to_csv(csv_buffer)
                s3_resource = boto3.resource("s3")
                s3_resource.Object(
                    bucket, f"{RUNNAME}_ID_{randint(10000000,99999999)}_file{int(x / SAVE_EVERY)}.csv"
                ).put(Body=csv_buffer.getvalue())
            else:
                if not os.path.exists(DATAPATH):
                    os.mkdir(DATAPATH)

                fullname = os.path.join(
                    DATAPATH, f"{RUNNAME}_ID_{randint(10000000,99999999)}_file{int(x / SAVE_EVERY)}.csv")

                rec.df().to_csv(fullname)
            rec.clear()


main()
