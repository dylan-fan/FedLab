import torchvision.transforms as transforms
import torchvision
import torch
import argparse
import sys

sys.path.append('../../../')
# sys.path.append('/home/zengdun/FedLab/')

from fedlab_core.client.topology import ClientAsyncTop
from fedlab_core.client.handler import ClientSGDHandler
from fedlab_utils.dataset.sampler import DistributedSampler
from models.lenet import LeNet


def get_dataset(args, dataset='MNIST', transform=None, root='../../dataset/mnist/'):
    """
    :param dataset_name:
    :param transform:
    :param batch_size:
    :return: iterators for the datasetaccuracy_score
    """
    train_transform = transforms.Compose([
        transforms.ToTensor(),
    ])

    test_transform = transforms.Compose([
        transforms.ToTensor(),
    ])
    trainset = torchvision.datasets.MNIST(
        root=root, train=True, download=True, transform=train_transform)
    testset = torchvision.datasets.MNIST(
        root=root, train=False, download=True, transform=test_transform)
   
    trainloader = torch.utils.data.DataLoader(trainset, sampler=DistributedSampler(trainset, rank=args.local_rank, num_replicas=args.world_size-1),
                                              batch_size=128,
                                              drop_last=True, num_workers=2)
    testloader = torch.utils.data.DataLoader(testset, batch_size=len(testset),
                                             drop_last=False, num_workers=2, shuffle=False)
    return trainloader, testloader


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Distbelief training example')
    parser.add_argument('--server_ip', type=str, default='127.0.0.1')
    parser.add_argument('--server_port', type=str, default='3002')
    parser.add_argument('--local_rank', type=int, default=1)
    parser.add_argument('--world_size', type=int, default=2)
    args = parser.parse_args()
    args.cuda = False

    model = LeNet()

    trainloader, testloader = get_dataset(args)

    handler = ClientSGDHandler(model, trainloader, cuda=args.cuda)
    top = ClientAsyncTop(client_handler=handler, server_addr=(
        args.server_ip, args.server_port), world_size=args.world_size, rank=args.local_rank)
    top.run()
