import gym

#given environment, number of episodes and timesteps, run environment and return sarsa or sar trajectories
def collect_traj(env, episodes, timesteps=None, sarsa=True):
	trajectories = []
	for i_episode in range(episodes):
		observation = env.reset()
		t = 0
		sar_traj = []
		while timesteps == None or t < timesteps:
			env.render()
			action = env.action_space.sample()  # random sample of action space
			observation, reward, done, info = env.step(action)
			sar_traj.append([observation, action, reward])
			if done:
				print("Episode finished after {} timesteps".format(t + 1))
				break
			t = t + 1
			if sarsa:
				trajectories.append(sar_to_sarsa(sar_traj))
			else:
				trajectories.append(sar_traj)
		env.close()
	return trajectories

#convert sar to sarsa trajectories
def sar_to_sarsa(sar_traj):
	sarsa_traj = []
	for i in range(len(sar_traj)):
		if i != 0:
			sarsa_traj[len(sarsa_traj) - 1].append(sar_traj[i][0])
			sarsa_traj[len(sarsa_traj) - 1].append(sar_traj[i][1])
		if i != len(sar_traj) - 1:
			sarsa_traj.append(sar_traj[i])
	return sarsa_traj

def main():
	#example()
	#loop()
	#space()
	#sample_space()
	#get_envs()
	#collect_traj()
	# sar = [["s1", "a1", "r1"], ["s2", "a2", "r2"], ["s3", "a3", "r3"], ["s4", "a4", "r4"]]
	# sarsa = sar_to_sarsa(sar)
	# print(sarsa)
	env = gym.make('LunarLander-v2')
	sarsa = collect_traj(env, 20, 100, True)
	print(sarsa)




if __name__ == '__main__':
	main()