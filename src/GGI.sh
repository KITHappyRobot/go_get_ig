xterm -geometry 80x5+0+0 -e "/opt/ros/kinetic/bin/roslaunch turtlebot_bringup minimal.launch" &
sleep 7s
xterm -geometry 80x5+0+120 -e "/opt/ros/kinetic/bin/roslaunch turtlebot_bringup 3dsensor.launch" &
sleep 7s
xterm -geometry 80x5+600+0 -e "/opt/ros/kinetic/bin/roslaunch turtlebot_navigation gmapping_demo.launch" &
sleep 7s
#xterm -geometry 80x5+600+120 -e "/opt/ros/kinetic/bin/roslaunch turtlebot_rviz_launchers view_navigation.launch" &
#sleep 7s
xterm -geometry 80x5+0+620 -e "/opt/ros/kinetic/bin/roslaunch manipulation motor_setup.launch"&
sleep 7s
xterm -geometry 80x5+0+220 -e "/opt/ros/kinetic/bin/rosrun reconfigure_inflation reconfigure_inflation_server.py " &
sleep 5s
xterm -geometry 80x50+600+220 -e "/opt/ros/kinetic/bin/rosrun chaser chaser.cpp" &
sleep 2s
xterm -geometry 80x5+600+320 -e "/opt/ros/kinetic/bin/rosrun go_get_it ggi_naigation.py" &
sleep 2s
xterm -geometry 80x7+600+420 -e "/opt/ros/kinetic/bin/rosrun go_get_it ggi_master.py"&
sleep 3s
xterm -geometry 80x5+0+320 -e "/opt/ros/kinetic/bin/rosrun e_object_recognizer object_recognizer.py" &
sleep 3s
xterm -geometry 80x5+0+420 -e "/opt/ros/kinetic/bin/rosrun e_grasping_position_detector e_grasping_position_detector" &
sleep 3s
xterm -geometry 80x5+0+520 -e "/opt/ros/kinetic/bin/rosrun manipulation manipulation.py" &
sleep 3s
xterm -geometry 80x5+0+220 -e "/opt/ros/kinetic/bin/rosrun go_get_it lp_gogetit.py" &
sleep 3s
xterm -geometry 80x5+0+220 -e "/opt/ros/kinetic/bin/rosrun go_get_it speech_recog.py" &
sleep 3s
