#######################################################################################################################
# Dokkan Battle Damage Taken Calculator 
# Goals :
#           Create backend for calculating the damage taken      
#           Build a frontend to display the program to users allowing them to easily use the application 
#           Have a UI to select specific bosses 
#           Be constantly up to date with hard bosses
#######################################################################################################################
from flask import Flask, render_template, request, session
import random  # Import the random module
import math

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for session management

# Define types and classes
type_indices = {'AGL': 1, 'STR': 2, 'PHY': 3, 'INT': 4, 'TEQ': 5}
types = list(type_indices.keys())
classes = ['Super', 'Extreme']

bosses = {
    "boss_1": {"name": "STR SSB Gogeta", "attack" : 3600000, "image" : "/static/assets/BossImages/STR_SSB_Gogeta.png.png"},
    "boss_2": {"name": "PHY Gohan (Beast)", "attack" : 2450000, "image" : "/static/assets/BossImages/PHY_Gohan_(Beast).png"},
    "boss_3": {"name": "STR Goku & Frieza", "attack" : 2850000, "image" : "/static/assets/BossImages/STR_Goku_&_Frieza.png"},
    "boss_4": {"name": "STR Goku & Frieza (Under 50%)", "attack" : 5700000, "image" : "/static/assets/BossImages/STR_Goku_&_Frieza_(Under 50%).png"},
    "boss_5": {"name": "TEQ Super Gogeta", "attack" : 4500000, "image" : "/static/assets/BossImages/TEQ_Super_Gogeta.png"},
    #"boss_1": {"name": "Empty", "attack" : 3600000, "image" : "/static/assets/BossImages/IMAGENAME.png"},
    #"boss_1": {"name": "Empty", "attack" : 3600000, "image" : "/static/assets/BossImages/IMAGENAME.png"},
    #"boss_1": {"name": "Empty", "attack" : 3600000, "image" : "/static/assets/BossImages/IMAGENAME.png"},
    #"boss_1": {"name": "Empty", "attack" : 3600000, "image" : "/static/assets/BossImages/IMAGENAME.png"},
    #"boss_1": {"name": "Empty", "attack" : 3600000, "image" : "/static/assets/BossImages/IMAGENAME.png"},

}

@app.template_filter('format_number')
def format_number(value):
    """Format number with commas as thousands separators."""
    return "{:,}".format(value)

@app.route('/', methods=['GET', 'POST'])
def index():
    # Initialize a nested dictionary for damage outputs
    damage_outputs = {type_: {cls: 0 for cls in classes} for type_ in types}  # Store a single value

    if request.method == 'POST':
        # Get the form data
        boss_attack = int(request.form['boss_attack'])

        # Safely handle damageReduction input
        damage_reduction_input = request.form.get('damageReduction', '')  # Default to empty string if not provided

        # Check if damage_reduction_input is a valid number, otherwise default to 0
        try:
            damage_reduction_input = int(damage_reduction_input) if damage_reduction_input.strip() else 0
        except ValueError:
            damage_reduction_input = 0  # Default to 0 if conversion fails

        unit_defense = int(request.form['unit_defense'])
        unit_type = request.form['unit_type']
        unit_class = request.form['unit_class']
        boss_select = request.form['boss_select']
        passive_guard = 'passive_guard' in request.form  # Check box for passive guard 

        # Store input values in session
        session['boss_select'] = boss_select
        session['boss_attack'] = boss_attack
        session['damageReduction'] = damage_reduction_input  # Store original percentage value (0-100)
        session['unit_defense'] = unit_defense
        session['unit_type'] = unit_type
        session['unit_class'] = unit_class
        session['passive_guard'] = passive_guard

        # Convert damage reduction from percentage to decimal for calculations
        damage_reduction = damage_reduction_input / 100.0

        # Calculate damage for all combinations of types and classes
        for type_ in types:
            # Calculate damage for Super class
            super_multiplier = get_type_multiplier(unit_type, type_, unit_class, boss_class='Super', passive_guard=passive_guard)
            damage_outputs[type_]['Super'] = calculate_damage(boss_attack, damage_reduction, unit_defense, super_multiplier, boss_type=type_, unit_type=unit_type, passive_guard=passive_guard)
            
            # Calculate damage for Extreme class
            extreme_multiplier = get_type_multiplier(unit_type, type_, unit_class, boss_class='Extreme', passive_guard=passive_guard)
            damage_outputs[type_]['Extreme'] = calculate_damage(boss_attack, damage_reduction, unit_defense, extreme_multiplier, boss_type=type_, unit_type=unit_type, passive_guard=passive_guard)

    else:
        # Pre-fill form with session data if available
        boss_select = session.get('boss_select', '')
        boss_attack = session.get('boss_attack', '')
        damage_reduction_input = session.get('damageReduction', 0)  # Default to 0 if not available
        unit_defense = session.get('unit_defense', '')
        unit_type = session.get('unit_type', '')
        unit_class = session.get('unit_class', '')
        passive_guard = session.get('passive_guard', False)

    return render_template('index.html', 
                           damage_outputs=damage_outputs,
                           boss_select=boss_select,
                           bosses=bosses,
                           boss_attack=boss_attack,
                           damage_reduction=damage_reduction_input,  # Keep original input value for display
                           unit_defense=unit_defense,
                           unit_type=unit_type,
                           unit_class=unit_class,
                           passive_guard=passive_guard)
def get_type_multiplier(unit_type, boss_type, unit_class, boss_class, passive_guard):
    if passive_guard:  # If Passive Guard is enabled
        return 0.8  # Passive Guard multiplier for all types
    
    unit_index = type_indices[unit_type]
    boss_index = type_indices[boss_type]

    # Determine type interaction (neutral, advantage, disadvantage)
    if unit_index == boss_index:  # Neutral type
        type_multiplier = 1.0 if unit_class == boss_class else 1.15
    elif (unit_index % 5) + 1 == boss_index:  # Advantage 
        type_multiplier = 1.25 if unit_class == boss_class else 1.5
    elif (boss_index % 5) + 1 == unit_index:  # Disadvantage 
        type_multiplier = 0.9 if unit_class == boss_class else 1.0
    else:  # Neutral interaction
        type_multiplier = 1.0 if unit_class == boss_class else 1.15

    return type_multiplier

def calculate_damage(boss_attack, damage_reduction, unit_defense, type_multiplier, boss_type, unit_type, passive_guard):
    if passive_guard:
        guard_multiplier = 0.5
    else:
        # Determine the type interaction for guard multiplier
        if (type_indices[unit_type] % 5) + 1 == type_indices[boss_type]:  # Type disadvantage
            guard_multiplier = 1.0  # Taking more damage
        elif (type_indices[boss_type] % 5) + 1 == type_indices[unit_type]:  # Type advantage
            guard_multiplier = 0.5  # Taking less damage
        else:  # Neutral interaction
            guard_multiplier = 1.0  # No change in damage
    
    # Dokkan avg. damage variance
    damage_variance = 1.015
    
    # Final damage calculation with damage reduction and guard multiplier
    final_damage = (boss_attack * (1 - damage_reduction) * type_multiplier * damage_variance - unit_defense) * guard_multiplier
    
    # Ensure damage is not negative; if it is, set it to a random value between 9 and 132 ("Double Digit damage")
    if final_damage <= 0:
        final_damage = random.randint(9, 132)

    return math.ceil(final_damage)  # Round the damage to the nearest integer

if __name__ == '__main__':
    app.run(debug=True)
