import React, { useEffect, useState } from 'react';
import { motion, AnimatePresence, useSpring, useTransform } from 'framer-motion';
import { X, CheckCircle } from 'lucide-react';

const Control3DPopup = ({ isOpen, onClose, controlType, controlName, action }) => {
    const [animationComplete, setAnimationComplete] = useState(false);

    useEffect(() => {
        if (isOpen) {
            setAnimationComplete(false);
            const timer = setTimeout(() => {
                setAnimationComplete(true);
            }, 2500);
            return () => clearTimeout(timer);
        }
    }, [isOpen]);

    const getAnimationConfig = () => {
        switch (controlType) {
            case 'pipe':
                return {
                    title: 'Water Pipe Control',
                    color: 'blue',
                    gradient: 'from-blue-500 to-cyan-500',
                    bgGlow: 'bg-blue-500/20',
                    animation: 'pipe'
                };
            case 'lights':
                return {
                    title: 'Lighting System',
                    color: 'yellow',
                    gradient: 'from-yellow-500 to-orange-500',
                    bgGlow: 'bg-yellow-500/20',
                    animation: 'lights'
                };
            case 'dustbin':
                return {
                    title: 'Waste Compactor',
                    color: 'green',
                    gradient: 'from-green-500 to-emerald-500',
                    bgGlow: 'bg-green-500/20',
                    animation: 'dustbin'
                };
            case 'ac':
                return {
                    title: 'Air Conditioning',
                    color: 'cyan',
                    gradient: 'from-cyan-500 to-blue-500',
                    bgGlow: 'bg-cyan-500/20',
                    animation: 'ac'
                };
            case 'ventilation':
                return {
                    title: 'Ventilation System',
                    color: 'purple',
                    gradient: 'from-purple-500 to-pink-500',
                    bgGlow: 'bg-purple-500/20',
                    animation: 'ventilation'
                };
            default:
                return {
                    title: 'System Control',
                    color: 'gray',
                    gradient: 'from-gray-500 to-slate-500',
                    bgGlow: 'bg-gray-500/20',
                    animation: 'default'
                };
        }
    };

    const config = getAnimationConfig();

    // Physics-based spring configurations (Cascadeur-style)
    const springConfig = {
        stiff: { type: "spring", stiffness: 400, damping: 30 },
        bouncy: { type: "spring", stiffness: 300, damping: 20, mass: 0.8 },
        smooth: { type: "spring", stiffness: 200, damping: 25, mass: 1 },
        heavy: { type: "spring", stiffness: 150, damping: 15, mass: 2 },
        fluid: { type: "spring", stiffness: 100, damping: 10, mass: 0.5 }
    };

    // CSS 3D Animation Component
    const AnimationDisplay = () => {
        if (controlType === 'pipe') {
            return (
                <div className="relative w-64 h-64 flex items-center justify-center" style={{ perspective: '800px' }}>
                    <div className="relative" style={{ transformStyle: 'preserve-3d' }}>
                        {/* Vertical Pipe with 3D depth */}
                        <motion.div
                            className="absolute left-1/2 -translate-x-1/2 w-16 h-48 bg-gradient-to-br from-gray-300 via-gray-500 to-gray-700 rounded-lg shadow-2xl"
                            style={{
                                transform: 'rotateY(25deg) rotateX(5deg)',
                                transformStyle: 'preserve-3d',
                                boxShadow: '0 20px 60px rgba(0,0,0,0.5), inset 0 2px 10px rgba(255,255,255,0.3)'
                            }}
                            initial={{ rotateY: 0 }}
                            animate={{ rotateY: 25 }}
                            transition={springConfig.smooth}
                        >
                            {/* Metallic shine effect */}
                            <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent rounded-lg"
                                style={{ transform: 'translateZ(1px)' }} />
                            {/* Pipe segments */}
                            {[...Array(4)].map((_, i) => (
                                <div key={i} className="absolute w-full h-0.5 bg-gray-800/50"
                                    style={{ top: `${(i + 1) * 20}%` }} />
                            ))}
                        </motion.div>

                        {/* Physics-based Water Flow with Gravity */}
                        {action !== 'off' && (
                            <div className="absolute left-1/2 -translate-x-1/2 top-0 w-full h-full">
                                {[...Array(12)].map((_, i) => (
                                    <motion.div
                                        key={i}
                                        className="absolute w-4 h-4 bg-blue-400 rounded-full"
                                        style={{
                                            filter: 'blur(2px)',
                                            boxShadow: '0 0 10px rgba(59, 130, 246, 0.8)',
                                            left: '50%',
                                            marginLeft: `${Math.sin(i) * 8}px`
                                        }}
                                        initial={{ y: -10, x: 0, scale: 0.5, opacity: 0 }}
                                        animate={{
                                            y: [0, 50, 120, 200],
                                            x: [0, Math.sin(i * 0.5) * 10, Math.sin(i * 0.5) * 15, Math.sin(i * 0.5) * 20],
                                            scale: [0.5, 1, 0.8, 0.3],
                                            opacity: [0, 1, 0.8, 0]
                                        }}
                                        transition={{
                                            duration: 2,
                                            repeat: Infinity,
                                            delay: i * 0.15,
                                            ease: [0.25, 0.46, 0.45, 0.94], // Cascadeur-style easing
                                            times: [0, 0.3, 0.7, 1]
                                        }}
                                    />
                                ))}
                                {/* Water splash at bottom */}
                                {[...Array(6)].map((_, i) => (
                                    <motion.div
                                        key={`splash-${i}`}
                                        className="absolute w-2 h-2 bg-blue-300/60 rounded-full"
                                        style={{ bottom: 0, left: '50%' }}
                                        initial={{ y: 0, x: 0, opacity: 0 }}
                                        animate={{
                                            y: [-5, -20, -10, 0],
                                            x: [(i - 3) * 5, (i - 3) * 15, (i - 3) * 20, (i - 3) * 15],
                                            opacity: [0, 0.8, 0.4, 0]
                                        }}
                                        transition={{
                                            duration: 1.2,
                                            repeat: Infinity,
                                            delay: i * 0.1,
                                            ease: "easeOut"
                                        }}
                                    />
                                ))}
                            </div>
                        )}

                        {/* Valve with realistic rotation physics */}
                        <motion.div
                            className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 w-20 h-20 bg-gradient-to-br from-red-400 via-red-600 to-red-800 rounded-full shadow-xl flex items-center justify-center"
                            style={{
                                transformStyle: 'preserve-3d',
                                boxShadow: '0 10px 40px rgba(239, 68, 68, 0.5), inset 0 2px 8px rgba(255,255,255,0.2)'
                            }}
                            initial={{ rotate: 0, scale: 1 }}
                            animate={{
                                rotate: action === 'off' ? 90 : 0,
                                scale: action === 'off' ? 0.95 : 1
                            }}
                            transition={springConfig.bouncy}
                        >
                            {/* Valve handle */}
                            <motion.div
                                className="w-16 h-2 bg-gray-900 rounded-full shadow-inner"
                                animate={{ scaleX: action === 'off' ? 0.9 : 1 }}
                                transition={springConfig.stiff}
                            />
                            <motion.div
                                className="w-2 h-16 bg-gray-900 rounded-full absolute shadow-inner"
                                animate={{ scaleY: action === 'off' ? 0.9 : 1 }}
                                transition={springConfig.stiff}
                            />
                            {/* Center bolt */}
                            <div className="absolute w-6 h-6 bg-gray-800 rounded-full shadow-lg" />
                        </motion.div>

                        {/* Pressure indicator */}
                        <motion.div
                            className="absolute -right-16 top-1/2 -translate-y-1/2 w-12 h-24 bg-gray-800/80 rounded-lg border-2 border-gray-600 overflow-hidden"
                            initial={{ opacity: 0, x: -20 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={springConfig.smooth}
                        >
                            <motion.div
                                className="absolute bottom-0 w-full bg-gradient-to-t from-blue-500 to-cyan-400"
                                initial={{ height: '0%' }}
                                animate={{ height: action === 'off' ? '0%' : '75%' }}
                                transition={springConfig.fluid}
                            />
                        </motion.div>
                    </div>
                </div>
            );
        }

        if (controlType === 'lights') {
            return (
                <div className="relative w-64 h-64 flex items-center justify-center" style={{ perspective: '800px' }}>
                    <div className="relative" style={{ transformStyle: 'preserve-3d' }}>
                        {/* Bulb Glass with physics-based glow */}
                        <motion.div
                            className="w-32 h-40 bg-gradient-to-b from-yellow-200 to-yellow-400 rounded-t-full relative"
                            style={{
                                borderBottomLeftRadius: '20%',
                                borderBottomRightRadius: '20%',
                                transformStyle: 'preserve-3d'
                            }}
                            initial={{ opacity: 0.3, scale: 0.9 }}
                            animate={{
                                opacity: action === 'off' ? 0.3 : 1,
                                scale: action === 'off' ? 0.95 : [1, 1.02, 1],
                                boxShadow: action === 'off'
                                    ? '0 0 0px 0px rgba(250, 204, 21, 0)'
                                    : ['0 0 40px 15px rgba(250, 204, 21, 0.4)', '0 0 60px 25px rgba(250, 204, 21, 0.7)', '0 0 40px 15px rgba(250, 204, 21, 0.4)']
                            }}
                            transition={{
                                ...springConfig.smooth,
                                boxShadow: { duration: 2, repeat: Infinity, ease: 'easeInOut' }
                            }}
                        >
                            {/* Filament with electric pulse */}
                            <motion.div
                                className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-16 h-20"
                                animate={{
                                    opacity: action === 'off' ? 0 : [0.8, 1, 0.8],
                                    scale: action === 'off' ? 0.8 : [1, 1.05, 1]
                                }}
                                transition={{ duration: 0.8, repeat: Infinity }}
                            >
                                <div className="w-full h-full border-4 border-orange-500 rounded-full"
                                    style={{ filter: 'drop-shadow(0 0 8px rgba(249, 115, 22, 0.8))' }} />
                                {/* Inner glow */}
                                <motion.div
                                    className="absolute inset-2 border-2 border-yellow-300 rounded-full"
                                    animate={{ opacity: action === 'off' ? 0 : [0.5, 1, 0.5] }}
                                    transition={{ duration: 1.5, repeat: Infinity }}
                                />
                            </motion.div>

                            {/* Glow Effect with physics */}
                            <motion.div
                                className="absolute inset-0 bg-yellow-300/50 rounded-t-full blur-xl"
                                animate={{
                                    opacity: action === 'off' ? 0 : [0.6, 0.9, 0.6],
                                    scale: action === 'off' ? 0.8 : [1, 1.1, 1]
                                }}
                                transition={{ duration: 2, repeat: Infinity, ease: 'easeInOut' }}
                            />

                            {/* Glass reflection */}
                            <div className="absolute inset-0 bg-gradient-to-br from-white/40 via-transparent to-transparent rounded-t-full"
                                style={{ transform: 'translateZ(2px)' }} />
                        </motion.div>

                        {/* Base with 3D depth */}
                        <motion.div
                            className="w-24 h-12 bg-gradient-to-b from-gray-300 to-gray-500 mx-auto"
                            style={{
                                transformStyle: 'preserve-3d',
                                boxShadow: '0 5px 15px rgba(0,0,0,0.3)'
                            }}
                            initial={{ rotateX: 0 }}
                            animate={{ rotateX: 5 }}
                            transition={springConfig.smooth}
                        >
                            <div className="w-full h-2 bg-gray-600" />
                            <div className="w-full h-2 bg-gray-500 mt-1" />
                            <div className="w-full h-2 bg-gray-600 mt-1" />
                        </motion.div>

                        {/* Enhanced Light Rays with physics */}
                        {action !== 'off' && (
                            <div className="absolute top-0 left-1/2 -translate-x-1/2 w-48 h-48 -z-10">
                                {[...Array(12)].map((_, i) => (
                                    <motion.div
                                        key={i}
                                        className="absolute top-1/2 left-1/2 w-3 h-40 bg-gradient-to-t from-yellow-400/70 via-yellow-300/40 to-transparent origin-bottom"
                                        style={{
                                            transform: `rotate(${i * 30}deg) translateX(-50%)`,
                                            filter: 'blur(3px)'
                                        }}
                                        initial={{ opacity: 0, scaleY: 0 }}
                                        animate={{
                                            opacity: [0, 0.8, 0.4, 0.8, 0],
                                            scaleY: [0, 1, 0.95, 1, 0]
                                        }}
                                        transition={{
                                            duration: 3,
                                            repeat: Infinity,
                                            delay: i * 0.15,
                                            ease: 'easeInOut'
                                        }}
                                    />
                                ))}
                            </div>
                        )}

                        {/* Photon particles */}
                        {action !== 'off' && (
                            <div className="absolute inset-0">
                                {[...Array(8)].map((_, i) => (
                                    <motion.div
                                        key={`photon-${i}`}
                                        className="absolute w-2 h-2 bg-yellow-300 rounded-full"
                                        style={{
                                            left: '50%',
                                            top: '30%',
                                            filter: 'blur(1px)'
                                        }}
                                        initial={{ opacity: 0, scale: 0 }}
                                        animate={{
                                            x: [0, Math.cos(i * 45 * Math.PI / 180) * 80],
                                            y: [0, Math.sin(i * 45 * Math.PI / 180) * 80],
                                            opacity: [0, 1, 0],
                                            scale: [0, 1, 0]
                                        }}
                                        transition={{
                                            duration: 1.5,
                                            repeat: Infinity,
                                            delay: i * 0.1,
                                            ease: 'easeOut'
                                        }}
                                    />
                                ))}
                            </div>
                        )}
                    </div>
                </div>
            );
        }

        if (controlType === 'dustbin') {
            return (
                <div className="relative w-64 h-64 flex items-center justify-center" style={{ perspective: '1000px' }}>
                    <div className="relative" style={{ transformStyle: 'preserve-3d' }}>
                        {/* Lid with physics-based movement */}
                        <motion.div
                            className="w-40 h-8 bg-gradient-to-b from-green-600 to-green-700 rounded-t-xl shadow-lg mb-2"
                            style={{
                                transformStyle: 'preserve-3d',
                                boxShadow: '0 5px 20px rgba(34, 197, 94, 0.4)'
                            }}
                            initial={{ y: 0, rotateX: 0 }}
                            animate={{
                                y: action === 'compress' ? [-10, -15, -12] : 0,
                                rotateX: action === 'compress' ? [-15, -20, -15] : 0
                            }}
                            transition={{
                                ...springConfig.bouncy,
                                repeat: action === 'compress' ? Infinity : 0,
                                repeatType: 'reverse',
                                duration: 1.5
                            }}
                        >
                            <div className="w-16 h-4 bg-green-800 rounded-full mx-auto mt-2 shadow-inner" />
                            {/* Lid shine */}
                            <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent rounded-t-xl" />
                        </motion.div>

                        {/* Bin Body with 3D perspective */}
                        <motion.div
                            className="w-36 h-48 bg-gradient-to-b from-green-500 to-green-700 rounded-b-xl relative overflow-hidden shadow-2xl mx-2"
                            style={{
                                transformStyle: 'preserve-3d',
                                transform: 'rotateY(15deg) rotateX(5deg)',
                                boxShadow: '0 20px 50px rgba(0,0,0,0.5), inset 0 2px 10px rgba(255,255,255,0.1)'
                            }}
                            animate={{
                                rotateY: action === 'compress' ? [15, 12, 15] : 15
                            }}
                            transition={{ duration: 1.5, repeat: action === 'compress' ? Infinity : 0 }}
                        >
                            {/* Waste Inside with gravity physics */}
                            <motion.div
                                className="absolute bottom-0 w-full bg-gradient-to-t from-gray-700 via-gray-600 to-gray-500"
                                initial={{ height: '70%' }}
                                animate={{
                                    height: action === 'compress' ? '30%' : '70%'
                                }}
                                transition={springConfig.heavy}
                            >
                                {/* Waste particles with individual physics */}
                                {[...Array(9)].map((_, i) => (
                                    <motion.div
                                        key={i}
                                        className="absolute bg-gray-800 rounded"
                                        style={{
                                            width: `${20 + Math.random() * 15}px`,
                                            height: `${20 + Math.random() * 15}px`,
                                            left: `${(i % 3) * 30 + 5}%`,
                                            top: `${Math.floor(i / 3) * 30}%`,
                                            boxShadow: '0 2px 5px rgba(0,0,0,0.3)'
                                        }}
                                        initial={{ scale: 1, rotate: 0 }}
                                        animate={{
                                            scale: action === 'compress' ? 0.4 : 1,
                                            y: action === 'compress' ? 30 : 0,
                                            rotate: action === 'compress' ? Math.random() * 90 : 0
                                        }}
                                        transition={{
                                            ...springConfig.heavy,
                                            delay: i * 0.05
                                        }}
                                    />
                                ))}

                                {/* Dust particles flying up */}
                                {action === 'compress' && [...Array(8)].map((_, i) => (
                                    <motion.div
                                        key={`dust-${i}`}
                                        className="absolute w-1 h-1 bg-gray-400 rounded-full"
                                        style={{ left: `${Math.random() * 100}%`, bottom: '10%' }}
                                        initial={{ y: 0, opacity: 0 }}
                                        animate={{
                                            y: [-10, -40, -60],
                                            x: [(Math.random() - 0.5) * 20, (Math.random() - 0.5) * 40],
                                            opacity: [0, 0.8, 0],
                                            scale: [0, 1, 0.5]
                                        }}
                                        transition={{
                                            duration: 1.5,
                                            repeat: Infinity,
                                            delay: i * 0.2,
                                            ease: 'easeOut'
                                        }}
                                    />
                                ))}
                            </motion.div>

                            {/* Compression Plate with hydraulic physics */}
                            {action === 'compress' && (
                                <motion.div
                                    className="absolute w-full h-12 bg-gradient-to-b from-gray-400 to-gray-600 shadow-xl"
                                    style={{
                                        boxShadow: '0 5px 20px rgba(0,0,0,0.5), inset 0 -2px 5px rgba(255,255,255,0.2)'
                                    }}
                                    initial={{ y: -100 }}
                                    animate={{ y: [60, 65, 60] }}
                                    transition={{
                                        ...springConfig.heavy,
                                        repeat: Infinity,
                                        repeatType: 'reverse',
                                        duration: 1.5
                                    }}
                                >
                                    {/* Hydraulic indicator */}
                                    <motion.div
                                        className="w-full h-2 bg-yellow-400"
                                        animate={{ opacity: [0.6, 1, 0.6] }}
                                        transition={{ duration: 0.5, repeat: Infinity }}
                                    />
                                    {/* Pressure lines */}
                                    {[...Array(3)].map((_, i) => (
                                        <div key={i} className="w-full h-0.5 bg-gray-700 mt-2" />
                                    ))}
                                </motion.div>
                            )}

                            {/* Bin texture */}
                            <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/5 to-transparent" />
                        </motion.div>

                        {/* Compression force indicator */}
                        {action === 'compress' && (
                            <motion.div
                                className="absolute -right-20 top-1/2 -translate-y-1/2 flex flex-col gap-1"
                                initial={{ opacity: 0, x: -10 }}
                                animate={{ opacity: 1, x: 0 }}
                                transition={springConfig.smooth}
                            >
                                {[...Array(5)].map((_, i) => (
                                    <motion.div
                                        key={i}
                                        className="w-12 h-1 bg-green-500 rounded-full"
                                        initial={{ scaleX: 0 }}
                                        animate={{ scaleX: [0, 1, 0.8, 1] }}
                                        transition={{
                                            duration: 0.8,
                                            repeat: Infinity,
                                            delay: i * 0.1
                                        }}
                                    />
                                ))}
                            </motion.div>
                        )}
                    </div>
                </div>
            );
        }

        if (controlType === 'ac') {
            return (
                <div className="relative w-64 h-64 flex items-center justify-center" style={{ perspective: '1000px' }}>
                    <div className="relative" style={{ transformStyle: 'preserve-3d' }}>
                        {/* AC Body with 3D depth */}
                        <motion.div
                            className="w-48 h-32 bg-gradient-to-b from-gray-100 to-gray-300 rounded-xl shadow-2xl relative"
                            style={{
                                transformStyle: 'preserve-3d',
                                boxShadow: '0 20px 50px rgba(0,0,0,0.4), inset 0 2px 10px rgba(255,255,255,0.5)'
                            }}
                            initial={{ rotateX: 0 }}
                            animate={{ rotateX: 10 }}
                            transition={springConfig.smooth}
                        >
                            {/* Vents with airflow effect */}
                            <div className="absolute inset-4 space-y-2">
                                {[...Array(6)].map((_, i) => (
                                    <motion.div
                                        key={i}
                                        className="w-full h-1.5 bg-gray-400 rounded-full relative overflow-hidden"
                                        style={{ boxShadow: 'inset 0 1px 2px rgba(0,0,0,0.3)' }}
                                    >
                                        {action !== 'off' && (
                                            <motion.div
                                                className="absolute inset-0 bg-gradient-to-r from-transparent via-cyan-300/50 to-transparent"
                                                initial={{ x: '-100%' }}
                                                animate={{ x: '200%' }}
                                                transition={{
                                                    duration: 1.5,
                                                    repeat: Infinity,
                                                    delay: i * 0.1,
                                                    ease: 'linear'
                                                }}
                                            />
                                        )}
                                    </motion.div>
                                ))}
                            </div>

                            {/* Display with realistic glow */}
                            <motion.div
                                className="absolute top-2 right-4 w-16 h-8 bg-black rounded flex items-center justify-center"
                                style={{
                                    boxShadow: action === 'off' ? 'none' : '0 0 10px rgba(34, 197, 94, 0.5)'
                                }}
                                animate={{ opacity: action === 'off' ? 0.3 : 1 }}
                                transition={springConfig.smooth}
                            >
                                <motion.span
                                    className="text-green-400 text-xs font-mono font-bold"
                                    animate={{
                                        opacity: action === 'off' ? 0 : [0.8, 1, 0.8],
                                        textShadow: action === 'off' ? 'none' : ['0 0 5px rgba(34, 197, 94, 0.5)', '0 0 10px rgba(34, 197, 94, 0.8)', '0 0 5px rgba(34, 197, 94, 0.5)']
                                    }}
                                    transition={{ duration: 2, repeat: Infinity }}
                                >
                                    {action === 'off' ? '' : '24°C'}
                                </motion.span>
                            </motion.div>

                            {/* Power indicator LED */}
                            <motion.div
                                className="absolute top-2 left-4 w-2 h-2 rounded-full"
                                style={{
                                    backgroundColor: action === 'off' ? '#ef4444' : '#22c55e',
                                    boxShadow: action === 'off' ? '0 0 5px #ef4444' : '0 0 10px #22c55e'
                                }}
                                animate={{ opacity: [0.6, 1, 0.6] }}
                                transition={{ duration: 1.5, repeat: Infinity }}
                            />
                        </motion.div>

                        {/* Fan Blades with realistic physics */}
                        <motion.div
                            className="absolute bottom-8 left-1/2 -translate-x-1/2 w-32 h-32"
                            style={{ transformStyle: 'preserve-3d' }}
                            initial={{ rotate: 0 }}
                            animate={{
                                rotate: action === 'off' ? 0 : 360,
                                opacity: action === 'off' ? 0.3 : 1,
                                scale: action === 'off' ? 0.95 : 1
                            }}
                            transition={{
                                rotate: {
                                    duration: action === 'off' ? 2 : 1.5,
                                    repeat: action === 'off' ? 0 : Infinity,
                                    ease: action === 'off' ? 'easeOut' : 'linear'
                                },
                                opacity: springConfig.smooth,
                                scale: springConfig.smooth
                            }}
                        >
                            {/* Center hub */}
                            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-8 h-8 bg-gray-700 rounded-full z-10"
                                style={{ boxShadow: '0 2px 10px rgba(0,0,0,0.5)' }} />

                            {/* Blades */}
                            {[...Array(4)].map((_, i) => (
                                <motion.div
                                    key={i}
                                    className="absolute top-1/2 left-1/2 w-4 h-16 bg-gradient-to-b from-cyan-400 to-blue-500 rounded-full origin-center"
                                    style={{
                                        transform: `rotate(${i * 90}deg) translateY(-50%)`,
                                        boxShadow: '0 2px 8px rgba(34, 211, 238, 0.4)'
                                    }}
                                    animate={{
                                        scaleY: action === 'off' ? 1 : [1, 1.05, 1]
                                    }}
                                    transition={{
                                        duration: 0.15,
                                        repeat: Infinity,
                                        delay: i * 0.0375
                                    }}
                                />
                            ))}
                        </motion.div>

                        {/* Cold Air Particles with fluid physics */}
                        {action !== 'off' && (
                            <div className="absolute bottom-0 left-1/2 -translate-x-1/2 w-full h-40">
                                {[...Array(15)].map((_, i) => (
                                    <motion.div
                                        key={i}
                                        className="absolute bg-cyan-300/40 rounded-full blur-md"
                                        style={{
                                            width: `${8 + Math.random() * 16}px`,
                                            height: `${8 + Math.random() * 16}px`,
                                            left: `${10 + (i % 5) * 18}%`,
                                            filter: 'blur(4px)'
                                        }}
                                        initial={{ y: 0, opacity: 0, scale: 0.5 }}
                                        animate={{
                                            y: [0, 30, 80, 120],
                                            x: [(Math.random() - 0.5) * 20, (Math.random() - 0.5) * 40, (Math.random() - 0.5) * 60],
                                            opacity: [0, 0.8, 0.5, 0],
                                            scale: [0.5, 1, 1.2, 0.8]
                                        }}
                                        transition={{
                                            duration: 3 + Math.random(),
                                            repeat: Infinity,
                                            delay: i * 0.2,
                                            ease: [0.25, 0.46, 0.45, 0.94]
                                        }}
                                    />
                                ))}

                                {/* Cold mist effect */}
                                {[...Array(3)].map((_, i) => (
                                    <motion.div
                                        key={`mist-${i}`}
                                        className="absolute w-32 h-8 bg-gradient-to-b from-cyan-200/20 to-transparent rounded-full"
                                        style={{ left: `${i * 25}%`, filter: 'blur(8px)' }}
                                        initial={{ y: 0, opacity: 0 }}
                                        animate={{
                                            y: [0, 60, 100],
                                            opacity: [0, 0.4, 0],
                                            scaleX: [1, 1.5, 2]
                                        }}
                                        transition={{
                                            duration: 4,
                                            repeat: Infinity,
                                            delay: i * 0.8,
                                            ease: 'easeOut'
                                        }}
                                    />
                                ))}
                            </div>
                        )}

                        {/* Temperature waves visualization */}
                        {action !== 'off' && (
                            <div className="absolute -left-20 top-1/2 -translate-y-1/2">
                                {[...Array(4)].map((_, i) => (
                                    <motion.div
                                        key={`wave-${i}`}
                                        className="absolute w-16 h-0.5 bg-cyan-400/60 rounded-full"
                                        initial={{ scaleX: 0, opacity: 0 }}
                                        animate={{
                                            scaleX: [0, 1, 0],
                                            opacity: [0, 0.8, 0],
                                            x: [0, 10, 20]
                                        }}
                                        transition={{
                                            duration: 1.5,
                                            repeat: Infinity,
                                            delay: i * 0.3,
                                            ease: 'easeInOut'
                                        }}
                                        style={{ top: `${i * 8}px` }}
                                    />
                                ))}
                            </div>
                        )}
                    </div>
                </div>
            );
        }

        // Default animation
        return (
            <div className="w-64 h-64 flex items-center justify-center">
                <motion.div
                    animate={{ scale: [1, 1.2, 1], rotate: [0, 180, 360] }}
                    transition={{ duration: 2, repeat: Infinity }}
                    className={`w-32 h-32 bg-gradient-to-br ${config.gradient} rounded-2xl shadow-2xl`}
                />
            </div>
        );
    };

    return (
        <AnimatePresence>
            {isOpen && (
                <>
                    {/* Backdrop */}
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        onClick={onClose}
                        className="fixed inset-0 bg-black/70 backdrop-blur-md z-50 flex items-center justify-center"
                    >
                        {/* Popup Card */}
                        <motion.div
                            initial={{ scale: 0.8, opacity: 0, y: 50 }}
                            animate={{ scale: 1, opacity: 1, y: 0 }}
                            exit={{ scale: 0.8, opacity: 0, y: 50 }}
                            transition={{ type: 'spring', duration: 0.6 }}
                            onClick={(e) => e.stopPropagation()}
                            className={`relative bg-gray-900/95 backdrop-blur-xl border-2 border-${config.color}-500/50 rounded-3xl p-8 max-w-lg w-full mx-4 shadow-2xl`}
                        >
                            {/* Close Button */}
                            <button
                                onClick={onClose}
                                className="absolute top-4 right-4 text-gray-400 hover:text-white transition-colors z-10"
                            >
                                <X size={28} />
                            </button>

                            {/* Title */}
                            <h2 className="text-2xl font-bold text-white text-center mb-2">
                                {config.title}
                            </h2>
                            <p className="text-gray-400 text-center mb-6">
                                {controlName} - {action === 'off' ? 'Turning Off' : action === 'on' ? 'Turning On' : 'Processing'}
                            </p>

                            {/* 3D Animation */}
                            <div className={`${config.bgGlow} rounded-2xl p-8 mb-6 flex items-center justify-center`}>
                                <AnimationDisplay />
                            </div>

                            {/* Status */}
                            <AnimatePresence>
                                {animationComplete && (
                                    <motion.div
                                        initial={{ opacity: 0, y: 20 }}
                                        animate={{ opacity: 1, y: 0 }}
                                        className={`bg-green-500/10 border border-green-500/30 rounded-xl p-4 flex items-center gap-3`}
                                    >
                                        <CheckCircle className="text-green-400" size={24} />
                                        <div>
                                            <p className="text-green-300 font-semibold">Action Completed</p>
                                            <p className="text-green-400/70 text-sm">
                                                {controlName} has been {action === 'off' ? 'turned off' : action === 'on' ? 'turned on' : 'processed'} successfully
                                            </p>
                                        </div>
                                    </motion.div>
                                )}
                            </AnimatePresence>

                            {/* Close Button */}
                            <button
                                onClick={onClose}
                                className={`mt-6 w-full py-3 bg-gradient-to-r ${config.gradient} rounded-xl font-bold text-white hover:shadow-lg transition-all uppercase tracking-wider`}
                            >
                                Close
                            </button>
                        </motion.div>
                    </motion.div>
                </>
            )}
        </AnimatePresence>
    );
};

export default Control3DPopup;
