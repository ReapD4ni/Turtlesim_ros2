# Turtlesim_ros2


Ebben a projektben egy hópelyhet szeretnék kirajzoltatni Ros2 környezetben a Turtlesim teknőcével.

snow.py egy script ami kirajzol egy hópelyhet.

konstruktor:
Publisher inicializálása a teknős mozgásának vezérléséhez. Subscription inicializálása egy olyan topichoz, ami Pose üzeneteket biztosít.

set_pen:
Létrehoz egy klienst a SetPen szolgáltatáshoz. Várja amíg a szolgáltatás elérhetővé válik. Meghívja a SetPen szolgáltatást aszinkron módon. Ellenőrzi a szolgáltatáshívás eredményét.

go_straight:
A teknős egyenes irányú irányításának alapvető funkciója, amelyet az órán tanultunk.

turn:
A teknős fordulásának alapvető funkciója, amelyet az órán tanultunk.

set_spawnpoint:
Egy olyan funkció, amely beállítja a teknős kiindulási helyzetét. Beállítja a tollat. Vár a pózinformációra. Kiszámolja a szöget és a távolságot a célponttól. Végrehajtja a mozgást és beállítja a toll attribútumait.

draw_snow:
Egy rekurzív függvény, aminek a paraméterei: sebesség, omega, számláló, távolság. Ha a számláló 0, a teknős egyenesen megy. Különben 3 rekurzív függvényhívás különböző omega értékekkel (a snow hópehelyhez 60, -120, 60 fokos fordulat szükséges).


![image](https://github.com/ReapD4ni/Turtlesim_ros2/assets/115945147/bb282284-8da8-42aa-a353-b2e423d6dd5c)
