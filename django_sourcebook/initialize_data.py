import json
import us

def dump_us_state_data():
    json_output = []
    states = [state for state in us.states.STATES_AND_TERRITORIES if not state.is_obsolete]
    for count, state in enumerate(states):
        state_info = {
            "pk": count + 1,
            "model": "sourcebook.state",
            "fields": {
                "fips_code": state.fips,
            }
        }
        json_output.append(state_info)
    with open("./initial_data/state_fips.json", "w") as f:
        json.dump(json_output, f)

if __name__ == "__main__":
    dump_us_state_data()