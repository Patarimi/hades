{ pkgs ? import <nixpkgs> {} }:

let
  inherit (pkgs) fetchFromGitHub callPackage;

  poetry2nix-src = fetchFromGitHub {
      owner = "nix-community";
      repo = "poetry2nix";
      rev = "2024.2.2230616";
      hash = "sha256-3Kq2l6xedw2BkvcASyAzNyjYRvupNiKxUvnBfcqOomM=";
  };

  poetry2nix = callPackage poetry2nix-src { };

in
  poetry2nix.mkPoetryPackages {
    projectDir = ./.;
    overrides = poetry2nix.defaultPoetryOverrides.extend
    (self: super: {
      gdstk = super.gdstk.overridePythonAttrs
      (
        old: {
          buildInputs = (old.buildInputs or [ ]) ++ [ super.setuptools ];
        }
      );
    });
  }

