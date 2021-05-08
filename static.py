vanguard_shelling = lambda position, shipcount: 1.0 if position >= shipcount else 0.5
vanguard_asw = lambda position, shipcount: 0.6 if position >= shipcount else 1

formation_modifiers_shelling = [0, 1.0, 0.8, 0.7, 0.75, 0.6, vanguard_shelling, 0, 0, 0, 0, 0.8, 1.0, 0.7, 1.1]
formation_modifiers_asw = [0, 0.6, 0.8, 1.2, 1.1 , 1.3, vanguard_asw, 0, 0, 0, 0, 1.3, 1.1, 1.0, 0.7]
engagement_modifiers = [0, 1, 0.8, 1.2, 0.6]
day_shelling_cap = 180
asw_cap = 150

day_cutin_modifiers = {
    "2": 1.2,
    "3": 1.1,
    "4": 1.2,
    "5": 1.3,
    "6": 1.5,
    "200": 1.35,
    "201": 1.3
}

night_cutin_modifiers = {

}