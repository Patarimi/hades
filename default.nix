{ pkgs ? import <nixpkgs> {} }:

let
  inherit (pkgs) fetchFromGitHub callPackage;

  poetry2nix-src = fetchFromGitHub {
      owner = "nix-community";
      repo = "poetry2nix";
      rev = "2024.2.618482";
      hash = "sha256-xPFxTMe4rKE/ZWLlOWv22qpGwpozpR+U1zhyf1040Zk=";
  };

  poetry2nix = callPackage poetry2nix-src { };

in
  poetry2nix.mkPoetryEnv {
    projectDir = ./.;
  }

