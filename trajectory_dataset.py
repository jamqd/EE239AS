from torch.utils.data import Dataset
import numpy as np
import torch
from collections.abc import Iterable

# I'm assuming we're using a dataloader to sample the data and perform gradient descent on it
# so this code is unbelievably simple. 
# hopefully it's what we need.


class TrajectoryDataset(Dataset):
    def __init__(self, init, max_replay_history, online = True):
        """
            param:
                trajectories: list of trajectories. assumes each trajectory is a list of sarsa tuples 
                max_replay_history: int indicating the max number of transitions (sarsa tuples) to store
        """
        # self.transitions = np.array([transition for trajectory in trajectories for transition in trajectory], dtype=float)
        if torch.cuda.is_available():
            self.transitions = torch.Tensor().cuda()
        else:
            self.transitions = torch.Tensor()

        self.trajectories = []
        self.buffer = []
        self.original_trajectories = []
        self.max_replay_history = max_replay_history
        self.transition_index = 0

        if online:
            self.add_transition(init)
            self.flush()
        else:
            self.add(init)

    def __len__(self):
        """
            param:
            return:
                number of transitions

        """
        return len(self.transitions)

    def __getitem__(self, idx):
        """
            param:
                idx: index of desired transition
            return:
                item at corresponding index in transitions
        """
        return self.transitions[idx]

    def add(self, trajectories):
        """
            param:
                trajectories: list of trajectories. assumes each trajectory is a list of sarsa tuples 
            return:
        """
        dim = sum([len(i) if isinstance(i, Iterable) else 1 for i in trajectories[0][0]])
        new_transitions = torch.zeros([sum([len(traj) for traj in trajectories]), dim], dtype=torch.float64)
        if torch.cuda.is_available():
            new_transitions = new_transitions.cuda()

        idx = 0
        for trajectory in trajectories:
            for transition in trajectory:
                s = transition[0]
                a = transition[1]
                r = transition[2]
                s_prime = transition[3]
                done = transition[4]
                
                if torch.cuda.is_available():
                    trans_tensor = torch.Tensor([*s,a,r,*s_prime,done]).cuda()
                else:
                    trans_tensor = torch.Tensor([*s,a,r,*s_prime,done])

                new_transitions[idx] = trans_tensor
                idx+=1

        if len(new_transitions) >= self.max_replay_history:
            self.transitions = new_transitions[len(new_transitions.float()) - self.max_replay_history:].float()
        elif len(new_transitions) + len(self.transitions) >= self.max_replay_history:
            old_start_index = (len(self.transitions.float()) + len(new_transitions.float())) - self.max_replay_history
            self.transitions = torch.cat((self.transitions[old_start_index:].float(),new_transitions.float()))
        else:
            self.transitions = torch.cat((self.transitions.float(), new_transitions.float()))
        self.add_trajectories(trajectories)

    def add_trajectories(self, trajectories):
        """
            param:
                trajectories: list of trajectories. assumes each trajectory is a list of sarsa tuples 
            return:
        """
        self.original_trajectories = self.restructure_original(self.original_trajectories + trajectories)

    def restructure_original(self, trajectories):
        """
            param:
                trajectories: list of trajectories composed of sarsa tuples
            return:
        """
        num_transitions = sum([len(trajectory) for trajectory in trajectories])
        idx_start = num_transitions - self.max_replay_history
        if idx_start > 0:
            idx_traj = 0
            next_trajectory = trajectories[idx_traj]
            while idx_start > len(next_trajectory):
                idx_start -= len(next_trajectory)
                idx_traj += 1
                next_trajectory = trajectories[idx_traj]
            if idx_traj <= len(trajectories) - 1:
                clipped_portion = trajectories[idx_traj][idx_start:]
                if clipped_portion:
                    return [clipped_portion] + trajectories[idx_traj + 1:]
                else:
                    return trajectories[idx_traj + 1:]
            else:
                return trajectories
        else:
            return trajectories

    def get_trajectories(self):
        """
            param:
            return:
                trajectories in their original formatting
        """
        return self.original_trajectories

    def add_transition(self, transition):
        """
            param:
                trans: transition to be added to transitions
        """
        self.buffer.append(transition)
        s = transition[0]
        a = transition[1]
        r = transition[2]
        s_prime = transition[3]
        done = transition[4]
        
        if torch.cuda.is_available():
            trans_tensor = torch.Tensor([*s,a,r,*s_prime,done]).cuda()
        else:
            trans_tensor = torch.Tensor([*s,a,r,*s_prime,done])    

        if self.transitions.size() == torch.Size([0]):
            self.transitions = trans_tensor.reshape([1,len(trans_tensor)])
        elif len(self.transitions) == self.max_replay_history:
            self.transitions[self.transition_index] = trans_tensor.reshape([1,len(trans_tensor)])
        else:
            self.transitions = torch.cat((self.transitions, trans_tensor.reshape([1,len(trans_tensor)])))
        self.transition_index += 1 
        self.transition_index = self.transition_index % self.max_replay_history
        

    def flush(self):
        # self.add_trajectories([self.buffer])
        self.buffer = []

#         Traceback (most recent call last):
#   File "./main.py", line 48, in <module>
#     main()
#   File "./main.py", line 44, in main
#     max_replay_history=args.max_replay
#   File "/home/graham/Documents/rl_project/train_dqn.py", line 87, in train
#     dataset = TrajectoryDataset(init_trajectories, max_replay_history=max_replay_history)
#   File "/home/graham/Documents/rl_project/trajectory_dataset.py", line 17, in __init__
#     self.transitions = np.array([transition for trajectory in trajectories for transition in trajectory], dtype=float)
# ValueError: setting an array element with a sequence.