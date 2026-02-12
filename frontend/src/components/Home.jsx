import React, { Suspense } from "react";
import { Canvas } from "@react-three/fiber";
import { useGLTF, Stage, PresentationControls, Environment, Float, Html } from "@react-three/drei";
import { useNavigate } from "react-router-dom";

// 1. Point to your LOCAL file in the public folder
const MODEL_PATH = "/porsche.glb"; 
useGLTF.preload(MODEL_PATH);

function PorscheModel(props) {
  // Pulls the file directly from your public folder
  const { scene } = useGLTF(MODEL_PATH);
  return <primitive object={scene} {...props} />;
}

function Loader() {
  return (
    <Html center>
      <div className="loader-container">
        <div className="spinner"></div>
        <p style={{ color: "white", marginTop: "10px", fontWeight: "bold" }}>Ignition Start...</p>
      </div>
    </Html>
  );
}

export default function Home() {
  const navigate = useNavigate();

  return (
    <div className="home-root">
      <div className="bg-glow"></div>
      <div className="home-container">
        <div className="hero-text-section">
          <h1 className="hero-title">
            GeoDrive <span className="text-gradient">AI</span>
          </h1>
          <p className="hero-description">
            Next-generation automotive intelligence. 
            Real-time spatial sentiment analysis.
          </p>
          <button className="launch-btn" onClick={() => navigate("/dashboard")}>
            Launch Engine
          </button>
        </div>

        <div className="hero-3d-section">
          <Canvas dpr={[1, 2]} shadows camera={{ position: [0, 0, 5], fov: 45 }}>
            <ambientLight intensity={1.5} />
            <spotLight position={[10, 10, 10]} angle={0.15} penumbra={1} />
            
            {/* Suspense handles the loading state */}
            <Suspense fallback={<Loader />}>
              <PresentationControls 
                speed={1.5} 
                global 
                zoom={0.7} 
                polar={[-0.1, Math.PI / 4]}
              >
                <Stage environment="city" intensity={0.5} contactShadow={false}>
                  <Float speed={1.5} rotationIntensity={0.5} floatIntensity={0.5}>
                    {/* .glb models are usually scaled better than .gltf */}
                    <PorscheModel scale={1} /> 
                  </Float>
                </Stage>
              </PresentationControls>
              <Environment preset="night" />
            </Suspense>
          </Canvas>
        </div>
      </div>
    </div>
  );
}