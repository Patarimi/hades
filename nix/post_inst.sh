#!/usr/bin/env /run/current-system/sw/bin/bash
sudo nix-channel --add https://nixos.org/channels/nixos-24.05 nixos
sudo nix-channel --update
sudo nixos-rebuild switch
