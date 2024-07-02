#!/usr/bin/env nix-shell
let
  nixpkgs = fetchTarball "https://github.com/NixOS/nixpkgs/tarball/nixos-24.05";
  source = import ./nix/sources.nix;
  pkgs = import source.nixpkgs  { };
  myAppEnv = pkgs.poetry2nix.mkPoetryEnv {
    projectDir = ./.;
    preferWheels = true;
  };
in myAppEnv.env.overrideAttrs (oldAttrs: {
  buildInputs = with pkgs; [
    ngspice
    klayout
    magic-vlsi
    python311Packages.meep
    hdf5
    h5utils
    imagemagick
    poetry
    ];
})
