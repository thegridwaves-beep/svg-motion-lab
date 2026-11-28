import React from "react";
import { Composition } from "remotion";
import { BridgeShort as Short, BRIDGE_FRAMES as FR } from "./videos/s/Bridge";
export const Root: React.FC = () => <Composition id="Sixty" component={Short} durationInFrames={FR} fps={30} width={1080} height={1920} />;
