# kc-damage-model
Models for simulating shelling phase damage and fitting special modifiers

For KC Damage Calculation, it is divided into six phases

## Basic Attack Power
### Daytime
There are three general calculations for daytime shelling
#### Basic Shelling
```python
BAP = base_FP + equip_FP + equip_bonus_FP + equip_imprv_FP_day + CF_const
```
`CF_const` is given by the following table and is 5 for player single fleet

|            | Enemy Single | Enemy CF |
|------------|--------------|----------|
| STF Main   | 10           | 2        |
| STF Escort | -5           | -5       |
| CTF Main   | 2            | 2        |
| CTF Escort | 10           | -5       |
| TCF Main   | -5           | -5       |
| TCF Escort | 10           | -5       |

#### Carrier Shelling
```python
FP = base_FP + equip_FP + equip_bonus_FP + equip_imprv_FP_day
TP = equip_TP + equip_imprv_TP
BAP = 55 + floor(1.5 * (FP + TP + floor(1.3 * equip_DB) + CF_const))
```
`CF_const` is the same as above. Equip bonus TP does not apply (likely due to ship stat being ignored). TP is set to 0 when attacking installations.

#### ASW
```python
BAP = (2 * sqrt(base_ASW) + equip_imprv_ASW + 1.5 * equip_ASW + stype_const) * syn1 * (1 + syn2 + syn3)
```
`stype_const` is 13 for DD/CL and 8 for AV, CVL, CAV, BBV. An exception is the Re-class BBV. `syn1` is 1.15 for sonar + DCP, `syn2` is 0.15 for sonar + DC and `syn3` is 0.1 for DCP + DC.

### Night
#### Basic Shelling
```python
FP = base_FP + equip_FP + equip_bonus_FP + equip_imprv_FP
TP = base_TP + equip_TP + equip_bonus_TP + equip_imprv_TP
BAP = FP + TP + night_contact
```
`night_contact` is 5 if night scout triggers. TP is 0 if attacking an installation.

#### Night Carrier Shelling
```python
np_mod1 = N * mod1
np_mod2 = mod2 * (equip_FP + equip_TP + equip_ASW + equip_DB)
BAP = base_FP + night_contact + sum_np(equip_FP + equip_TP + equip_DB + np_mod2 * sqrt(N) + np_mod1 + sqrt(equip_imprv))
```
`sum_np` is the sum of all night aircraft. Due to the calcualtion depending on the number of planes N and the mid-battle plane loss, this should not be used.

### Anti-installation
Applied after BAP but technically still part of BAP, since precap modifiers are applied after
```python
BAP = (BAP + add1) * mod + add2
```
Values and improvements to be added later

## Pre-cap attack power
### Daytime
```python
precap = BAP * health_modifier * formation_modifier * engagement_modifier + hidden_fits
```
### Night
```python
precap = BAP * health_modifier * special_attack_modifier
```
An exception for night ASW, those are treated as daytime attacks instead, for CF night and night-only battles.

## Attack Power Cap
```python
if precap > cap:
    capped = int(cap + sqrt(precap - cap))
else:
    capped = int(precap)
```
cap is 170 for ASW, 220 for day shelling and 360 for NB

## Critical Hit
```python
if critcal_hit:
    postcrit = int(precapped * 1.5 * air_prof)
else:
    postcrit = int(capped)
```
air_prof depends on CVCI and carrier proficiency, probably just fix to R7 all planes and constant number

## Post-cap attack power
### Anti-Installation Modifiers
```python
postcrit = postcrit * mod + add
```
SDH

### Daytime
```python
postcap = postcrit * arty_spotting_mod * AP_shell_mod
```

### Night
```python
postcap = postcrit
```
Currently no postcapped modifiers for night, except maybe special attack bonuses?
### PT imp
```python
postcap = postcap * PT_imp_modifier
```

## Actual Damage Calculation
```python
damage = int((postcap - armor_roll - armor_reduction) * remaining_ammo_modifier)
```

