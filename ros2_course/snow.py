import math
import rclpy
from rclpy.node import Node		#kommunikáció a ROS rendszer részeivel
from geometry_msgs.msg import Twist	#sebesség, elfordulás
from turtlesim.msg import Pose		#pozíció, orientáció
from turtlesim.srv import SetPen


class snow(Node):

    def __init__(self):
        super().__init__('Teki')	#ősosztály hívás
        self.twist_pub = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
        self.pose = None		#aktuális pozi null
        self.subscription = self.create_subscription(Pose, '/turtle1/pose', self.cb_pose, 10)

    def cb_pose(self, msg):		#aktuális pozício, orientáció mentése
        self.pose = msg

    def set_pen(self, r, g, b, width, off):
        pen_client = self.create_client(SetPen, '/turtle1/set_pen')
        while not pen_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('A set_pen szolgáltatás nem érhető el, vár...')
            self.get_logger().info('set_pen szolgáltatás elérhető.')
            
        req = SetPen.Request()
        req.r = r
        req.g = g
        req.b = b
        req.width = width
        req.off = off
        future = pen_client.call_async(req)
        rclpy.spin_until_future_complete(self, future)
        if future.result() is not None:
            self.get_logger().info('Toll beállítva.')
        else:
            self.get_logger().error('Hiba a toll beállításakor.')

    def go_straight(self, speed, distance):
        while self.pose is None and rclpy.ok():
            self.get_logger().info('Várakozás...')
            rclpy.spin_once(self)

        loop_rate = self.create_rate(100, self.get_clock()) # Hz

        x_start = self.pose.x
        y_start = self.pose.y

        x_end = x_start + distance * math.cos(self.pose.theta)
        y_end = y_start + distance * math.sin(self.pose.theta)

        vel_msg = Twist()
        vel_msg.linear.x = speed if distance > 0 else -speed	#sebesség beállítása
        vel_msg.linear.y = 0.0
        vel_msg.linear.z = 0.0
        vel_msg.angular.x = 0.0
        vel_msg.angular.y = 0.0
        vel_msg.angular.z = 0.0

        self.twist_pub.publish(vel_msg)

        while rclpy.ok():			#célpoz elérésének ellenőrzése
            current_displacement = math.sqrt((self.pose.x - x_start)**2 + (self.pose.y - y_start)**2)

            if current_displacement >= abs(distance):
                break

            self.twist_pub.publish(vel_msg)
            rclpy.spin_once(self)

        # Stop
        vel_msg.linear.x = 0.0
        self.twist_pub.publish(vel_msg)
        self.get_logger().info('Elérte vagy túllépte a távolságot.')




    def turn(self, omega, angle):
        ANGLE_TOLERANCE = math.radians(0.4)
        omega_rad = math.radians(omega)		#elfordulási sebesség

        while self.pose is None and rclpy.ok():
            self.get_logger().info('Kiinduló helyzetbe fordulva...')
            #rclpy.spin_once(self)

        angle_rad = math.radians(angle)		# elfordulási szög

        loop_rate = self.create_rate(100, self.get_clock())

        theta_start = self.pose.theta		# kezdőorinetáció mentése

        theta_target = theta_start + angle_rad	#célorientáció kiszámítása (előfordulási szögből)

        theta_target = (theta_target + math.pi) % (2 * math.pi) - math.pi

        vel_msg = Twist()
        vel_msg.linear.x = 0.0
        vel_msg.linear.y = 0.0
        vel_msg.linear.z = 0.0
        vel_msg.angular.x = 0.0
        vel_msg.angular.y = 0.0
        vel_msg.angular.z = omega_rad if angle_rad > 0 else -omega_rad	#elfordulási sebesség beállítása
									# az elfordulási irány függvényében
        self.twist_pub.publish(vel_msg)

        while rclpy.ok():
            current_angle_diff = (self.pose.theta - theta_target + math.pi) % (2 * math.pi) - math.pi

            adjustment_factor = max(abs(current_angle_diff) / angle_rad, 0.1)
            vel_msg.angular.z = omega_rad * adjustment_factor * (1 if angle_rad > 0 else -1)

            if abs(current_angle_diff) < ANGLE_TOLERANCE:
                break

            self.twist_pub.publish(vel_msg)
            rclpy.spin_once(self)

        vel_msg.angular.z = 0.0
        self.twist_pub.publish(vel_msg)
        self.get_logger().info('Elérte a célpozíciót.')

    
    def set_spawnpoint(self, speed, omega, x, y):
        self.set_pen(0, 0, 0, 0, 1)
        # Wait for position to be received
        loop_rate = self.create_rate(100, self.get_clock()) # Hz
        while self.pose is None and rclpy.ok():
            self.get_logger().info('Várom a pózt...')
            rclpy.spin_once(self)

        # Aktuális pozició mentés
        x0 = self.pose.x
        y0 = self.pose.y
        theta_0 = math.degrees(self.pose.theta)

        theta_1 = math.degrees(math.atan2(y-y0, x-x0))		#célorientáció számolás
        angle = theta_1 - theta_0				#elfordulási szög számolás
        distance = math.sqrt(((x - x0) * (x - x0)) + (y - y0) * (y - y0))

        # Mozgás végrehajtása
        self.turn(omega, angle)
        self.go_straight(speed, distance)

        self.set_pen(255, 255, 255, 5, 0)
    def draw_snow(self, speed, omega, I, L):	#sebesség, elfordulási sebesség, rekurzió méylsége, vonal hossz
        if I==0:
            self.go_straight(speed, L)
        else:
            self.draw_snow(speed, omega, I-1, L)
            self.turn(omega, 60)
            self.draw_snow(speed, omega, I-1, L)
            self.turn(omega, -120)
            self.draw_snow(speed, omega, I-1, L)
            self.turn(omega, 60)
            self.draw_snow(speed, omega, I-1, L)
            

def main(args=None):
    rclpy.init(args=args)
    s = snow()
    s.set_spawnpoint(5.0,400.0,6,9)
    s.turn(500, -155)
    for i in range(3):
        s.draw_snow(5.0,400.0,2,0.6)
        s.turn(500, -120)
    # Explicit módon semmisítse meg a csomópontot
    # (opcionális - különben automatikusan megtörténik

    # amikor a szemétgyűjtő megsemmisíti a csomópont objektumot)
    s.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
