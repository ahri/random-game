#!/usr/bin/env stack
{- stack --resolver lts-11.7 --install-ghc runghc
   --package regex-compat
   --package process
-}

-- https://downloads.haskell.org/~ghc/8.2.2/docs/html/users_guide/using-warnings.html
{-# OPTIONS_GHC -Werror -Wall -Wcompat                                #-}
{-# OPTIONS_GHC -Wincomplete-uni-patterns -Wincomplete-record-updates #-}
{-# OPTIONS_GHC -Widentities -Wredundant-constraints                  #-}
{-# OPTIONS_GHC -Wmonomorphism-restriction -Wmissing-home-modules     #-}
-- {-# OPTIONS_GHC -ddump-minimal-imports                             #-}

import             Control.Exception
import             System.Directory
import             System.Exit
import             System.IO
import             System.Process
import             System.Random
import             System.Win32.Registry
import             Text.Regex

newtype SteamDir = SteamDir FilePath deriving (Show, Eq)

newtype SteamAppId = SteamAppId String deriving (Show, Eq)

main :: IO ()
main = do
    steamPath <- findSteamPath >>= maybe
        (hPutStrLn stderr "Couldn't find Steam" >> exitFailure)
        return

    appIds <- steamAppIds steamPath
    randAppId <- (appIds !!) <$> getStdRandom (randomR (0, length appIds))

    _ <- openSteamStore steamPath randAppId

    exitSuccess


findSteamPath :: IO (Maybe SteamDir)
findSteamPath = do
    vals <- bracket
        (regOpenKey hKEY_CURRENT_USER "Software\\Valve\\Steam")
        regCloseKey
        regEnumKeyVals
    
    pure $ foldr f Nothing vals
      where
        f cur acc = case cur of
            ("SteamPath", path, _) -> Just $ SteamDir path
            _                      -> acc

steamAppIds :: SteamDir -> IO [SteamAppId]
steamAppIds (SteamDir sd) = filterSteamManifestsForIdentifiers <$> listDirectory (sd ++ "/steamapps")
  where
    filterSteamManifestsForIdentifiers :: [FilePath] -> [SteamAppId]
    filterSteamManifestsForIdentifiers = foldr f []

    f cur acc = case matchRegex manifestPattern cur of
        Just [appId] -> SteamAppId appId : acc
        _            -> acc

    manifestPattern :: Regex
    manifestPattern = mkRegex "^appmanifest_([0-9]+)\\.acf$"

openSteamStore :: SteamDir -> SteamAppId -> IO (Maybe Handle, Maybe Handle, Maybe Handle, ProcessHandle)
openSteamStore (SteamDir sd) (SteamAppId appId) =
    createProcess_ "steam" $ proc
        (sd ++ "/Steam.exe")
        ["steam://nav/games/details/" ++ appId]
