
from veronica_logic import CommonTower, HardTower, CommonEnemy, FastEnemy

levels_data = [


{
 'enemies':
    # olas de enemigos:
    {
     CommonEnemy: 20,
    },
 'initial towers':
    {
     CommonTower: [(10, 2), (10, 6)],
    },
 'initial resources': 100,
 },

{
 'enemies':
    {
     CommonEnemy: 20,
     FastEnemy: 10,
    },
 'initial towers':
    {
     CommonTower: [(10, 2), (10, 6)],
     HardTower: [(10, 10)]
    },
 'initial resources': 100,
 },

]

