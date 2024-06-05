#!/usr/bin/env nix-shell
let
  nixpkgs = fetchTarball "https://github.com/NixOS/nixpkgs/tarball/nixos-24.05";
  pkgs = import nixpkgs { config = {}; overlays = []; };
in

pkgs.mkShellNoCC {
  packages = with pkgs; [
    ngspice
    klayout
    magic-vlsi
    python311Packages.meep
    hdf5
    h5utils
    imagemagick
    poetry
  ];
  postInstall = ''poetry install'';
}
