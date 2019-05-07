import torch
import torch.nn as nn
import torch.nn.functional as F

class Res_Block(nn.Module):
    # building block can be reused for encoder and generator
    def __init__(self, in_channels=64, out_channels=64, avg=False, upsample=False):#groups=1, scale=1.0
        super(Res_Block, self).__init__()
        self.conv1 = nn.Conv2d(in_channels, out_channels, 3, 1, 1, bias=False)
        self.bn = nn.BatchNorm2d(out_channels)
        self.relu = nn.LeakyReLU(0.2, inplace=True)
        self.conv2 = nn.Conv2d(out_channels, out_channels, 3, 1, 1, bias=False)
        self.avg = avg
        self.avgpool = nn.AvgPool2d(2)
        self.upsample = upsample
        self.upsample_layer = nn.Upsample(scale_factor=2, mode='nearest')
        #self.in_channels = in_channels
        #self.out_channels = out_channels
        if in_channels > out_channels:
            self.sample = 1
            self.addon = nn.Conv2d(in_channels, out_channels, 1, 1, 0, bias=False)
        elif in_channels == out_channels:
            self.sample = 0
        else:
            self.sample = -1
            self.addon = nn.Conv2d(in_channels, out_channels, 1, 1, 0, bias=False)


    def forward(self, input):
        if self.sample == 0:
            residual = input
            output = self.relu(self.bn(self.conv1(input)))
            output = self.conv2(output)
            output += residual
            output = self.relu(self.bn(output))

        elif self.sample == -1: # for encoder, out_ch should be in_ch * 2
            residual = self.addon(input)
            output = self.relu(self.bn(self.conv1(input)))
            output = self.conv2(output)
            output += residual
            if self.avg == True:
                output = self.avgpool(output)

        else: # for generator, out_ch should be in_ch/2
            if self.upsample == True:
                input = self.upsample_layer(input)
            residual = self.addon(input)
            output = self.relu(self.bn(self.conv1(input)))
            output = self.conv2(output)
            output += residual
            output = self.relu(self.bn(output))

        return output


class Intro_enc(nn.Module):
    def __init__(self, num_col=3, img_dim=256, z_dim=512):#groups=1, scale=1.0
        super(Intro_enc, self).__init__()
        self.dim = img_dim
        self.nc = num_col
        self.c_dim = self.dim // 8
        self.net = nn.Sequential(
            nn.Conv2d(self.nc, self.c_dim, 5, 1, 2, bias=False),#
            nn.BatchNorm2d(self.c_dim),
            nn.LeakyReLU(0.2),
            nn.AvgPool2d(2),
        )
        self.fc = nn.Linear(z_dim * 4 * 4, 2 * z_dim)

        if self.dim == 256: # 32, 64, 128, 256, 512, 512
            # 32 * 128 * 128
            self.net.add_model('res64', Res_Block(32, 64, avg=True))# 64 * 64 * 64
            self.net.add_model('res128', Res_Block(64, 128, avg=True))# 128 * 32 * 32
            self.net.add_model('res256', Res_Block(128, 256, avg=True))# 256 * 16 * 16
            self.net.add_model('res512', Res_Block(256, 512, avg=True))# 512 * 8 * 8
            self.net.add_model('res512_', Res_Block(512, 512, avg=True))# 512 * 4 * 4

        elif self.dim == 128: # 16, 32, 64, 128, 256, 256
            # 16 * 64 * 64
            self.net.add_model('res64', Res_Block(16, 32, avg=True))# 32 * 32 * 32
            self.net.add_model('res64', Res_Block(32, 64, avg=True))# 64 * 16 * 16
            self.net.add_model('res128', Res_Block(64, 128, avg=True))# 128 * 8 * 8
            self.net.add_model('res256', Res_Block(128, 256, avg=True))# 256 * 4 * 4

    def forward(self, input):
        output = self.net(input)
        output = output.view(output.size(0), -1)# reshape
        output = self.fc(output)
        mu, logvar = output.chunk(2, dim=1)

        return mu, logvar



class Intro_gen(nn.Module):
    def __init__(self, img_dim=256, num_col=3, z_dim=512):#groups=1, scale=1.0
        super(Intro_gen, self).__init__()
        self.dim = img_dim
        self.nc = num_col
        self.z_dim = z_dim
        self.fc = nn.Linear(self.z_dim, self.z_dim * 4 * 4)
        self.relu = nn.ReLU(True)
        self.net = nn.Sequential()

        if self.z_dim == 512:
            self.net.add_module('res512-', Res_Block(512, 512))
            self.net.add_module('res256', Res_Block(512, 256, upsample=True))
            self.net.add_module('res128', Res_Block(256, 128, upsample=True))
            self.net.add_module('res64', Res_Block(128, 64, upsample=True))
            self.net.add_module('res32', Res_Block(64, 32, upsample=True))
            self.net.add_module('conv', nn.Conv2d(32, num_col, 5, 1, 2))

        elif self.z_dim == 256:
            self.net.add_module('res128', Res_Block(256, 128, upsample=True))
            self.net.add_module('res64', Res_Block(128, 64, upsample=True))
            self.net.add_module('res32', Res_Block(64, 32, upsample=True))
            self.net.add_module('res16', Res_Block(32, 16, upsample=True))
            self.net.add_module('conv', nn.Conv2d(16, num_col, 5, 1, 2))

    def forward(self, input):
        # input: latent vector
        output = self.net(input)
        # reshape
        output = output.view(self.z_dim, 4, 4)
        output = self.net(output)

        return output