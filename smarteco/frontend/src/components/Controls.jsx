import React, { useState, useEffect } from 'react';
import { GlassCard } from './UI';
import Control3DPopup from './Control3DPopup';
import { API_BASE_URL } from '../config';
import {
    Droplets, Lightbulb, Trash2, Wind, Thermometer,
    Power, Settings, Cpu, Wifi, Database, HardDrive,
    Zap, Fan, Sun, Moon
} from 'lucide-react';
import { motion } from 'framer-motion';

const Controls = () => {
    const [controlStates, setControlStates] = useState({});
    const [activePopup, setActivePopup] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchControlStates();
    }, []);

    const fetchControlStates = async () => {
        try {
            const response = await fetch(`${API_BASE_URL}/api/controls/status`);
            const data = await response.json();
            setControlStates(data.states || {});
            setLoading(false);
        } catch (error) {
            console.error('Failed to fetch control states:', error);
            // Initialize with default states
            setControlStates({
                pipe: true,
                lights_hw: true,
                dustbin: false,
                water_valve: true,
                lights_sw: true,
                ac: true,
                ventilation: true,
                heating: false
            });
            setLoading(false);
        }
    };

    const handleControl = async (device, type, action) => {
        // Show popup animation
        setActivePopup({ device, type, action });

        // Send control command to backend
        try {
            await fetch(`${API_BASE_URL}/api/controls/${type}/${device}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ action })
            });

            // Update local state
            setControlStates(prev => ({
                ...prev,
                [device]: action === 'on'
            }));
        } catch (error) {
            console.error('Control action failed:', error);
        }
    };

    const ControlButton = ({ icon: Icon, label, device, type, isActive, color = 'purple', action }) => {
        const colorMap = {
            blue: {
                bg: 'from-blue-500 to-cyan-500',
                hover: 'hover:shadow-blue-500/50',
                border: 'border-blue-500/30',
                text: 'text-blue-400',
                activeBg: 'bg-blue-500/20'
            },
            yellow: {
                bg: 'from-yellow-500 to-orange-500',
                hover: 'hover:shadow-yellow-500/50',
                border: 'border-yellow-500/30',
                text: 'text-yellow-400',
                activeBg: 'bg-yellow-500/20'
            },
            green: {
                bg: 'from-green-500 to-emerald-500',
                hover: 'hover:shadow-green-500/50',
                border: 'border-green-500/30',
                text: 'text-green-400',
                activeBg: 'bg-green-500/20'
            },
            purple: {
                bg: 'from-purple-500 to-pink-500',
                hover: 'hover:shadow-purple-500/50',
                border: 'border-purple-500/30',
                text: 'text-purple-400',
                activeBg: 'bg-purple-500/20'
            },
            cyan: {
                bg: 'from-cyan-500 to-blue-500',
                hover: 'hover:shadow-cyan-500/50',
                border: 'border-cyan-500/30',
                text: 'text-cyan-400',
                activeBg: 'bg-cyan-500/20'
            },
            red: {
                bg: 'from-red-500 to-orange-500',
                hover: 'hover:shadow-red-500/50',
                border: 'border-red-500/30',
                text: 'text-red-400',
                activeBg: 'bg-red-500/20'
            }
        };

        const colors = colorMap[color];

        return (
            <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => handleControl(device, type, action || (isActive ? 'off' : 'on'))}
                className={`relative p-6 rounded-2xl border-2 ${colors.border} transition-all ${colors.hover} hover:shadow-xl group ${isActive ? colors.activeBg : 'bg-gray-800/50'
                    }`}
            >
                {/* Status Indicator */}
                <div className="absolute top-3 right-3">
                    <div className={`w-3 h-3 rounded-full ${isActive ? 'bg-green-500 animate-pulse' : 'bg-gray-600'}`} />
                </div>

                {/* Icon */}
                <div className={`${colors.activeBg} w-16 h-16 rounded-xl flex items-center justify-center mb-4 mx-auto group-hover:scale-110 transition-transform`}>
                    <Icon size={32} className={colors.text} />
                </div>

                {/* Label */}
                <h3 className="text-white font-bold text-sm mb-1">{label}</h3>
                <p className="text-gray-400 text-xs">
                    {isActive ? 'Active' : 'Inactive'}
                </p>

                {/* Action Hint */}
                <div className={`mt-3 text-xs font-semibold ${colors.text} opacity-0 group-hover:opacity-100 transition-opacity`}>
                    Click to {action || (isActive ? 'Turn Off' : 'Turn On')}
                </div>
            </motion.button>
        );
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center h-96">
                <div className="text-center">
                    <Settings className="animate-spin text-purple-400 mx-auto mb-4" size={48} />
                    <p className="text-gray-400">Loading Controls...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="space-y-6 animate-fade-in">
            {/* Header */}
            <div className="flex justify-between items-center">
                <div>
                    <h2 className="text-3xl font-bold text-white mb-1">System Controls</h2>
                    <p className="text-gray-400">Manage hardware and software components</p>
                </div>
                <div className="flex items-center gap-2 px-4 py-2 bg-green-500/10 rounded-xl border border-green-500/20">
                    <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
                    <span className="text-xs text-green-400 font-semibold">ALL SYSTEMS OPERATIONAL</span>
                </div>
            </div>

            {/* Hardware Controls */}
            <GlassCard>
                <div className="flex items-center gap-3 mb-6">
                    <div className="p-3 bg-blue-500/10 rounded-xl">
                        <HardDrive className="text-blue-400" size={24} />
                    </div>
                    <div>
                        <h3 className="text-xl font-bold text-white">Hardware Controls</h3>
                        <p className="text-gray-400 text-sm">Physical device management</p>
                    </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                    <ControlButton
                        icon={Droplets}
                        label="Water Pipe"
                        device="pipe"
                        type="hardware"
                        isActive={controlStates.pipe}
                        color="blue"
                    />
                    <ControlButton
                        icon={Lightbulb}
                        label="Lighting System"
                        device="lights_hw"
                        type="hardware"
                        isActive={controlStates.lights_hw}
                        color="yellow"
                    />
                    <ControlButton
                        icon={Trash2}
                        label="Waste Compactor"
                        device="dustbin"
                        type="hardware"
                        isActive={controlStates.dustbin}
                        color="green"
                        action="compress"
                    />
                    <ControlButton
                        icon={Droplets}
                        label="Water Valve"
                        device="water_valve"
                        type="hardware"
                        isActive={controlStates.water_valve}
                        color="cyan"
                    />
                </div>
            </GlassCard>

            {/* Software Controls */}
            <GlassCard>
                <div className="flex items-center gap-3 mb-6">
                    <div className="p-3 bg-purple-500/10 rounded-xl">
                        <Cpu className="text-purple-400" size={24} />
                    </div>
                    <div>
                        <h3 className="text-xl font-bold text-white">Software Controls</h3>
                        <p className="text-gray-400 text-sm">Automated system management</p>
                    </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                    <ControlButton
                        icon={Lightbulb}
                        label="Smart Lights"
                        device="lights_sw"
                        type="software"
                        isActive={controlStates.lights_sw}
                        color="yellow"
                    />
                    <ControlButton
                        icon={Wind}
                        label="Air Conditioning"
                        device="ac"
                        type="software"
                        isActive={controlStates.ac}
                        color="cyan"
                    />
                    <ControlButton
                        icon={Fan}
                        label="Ventilation"
                        device="ventilation"
                        type="software"
                        isActive={controlStates.ventilation}
                        color="purple"
                    />
                    <ControlButton
                        icon={Thermometer}
                        label="Heating System"
                        device="heating"
                        type="software"
                        isActive={controlStates.heating}
                        color="red"
                    />
                </div>
            </GlassCard>

            {/* System Status */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <GlassCard className="border-l-4 border-l-green-500">
                    <div className="flex items-center gap-3">
                        <Power className="text-green-400" size={32} />
                        <div>
                            <p className="text-gray-400 text-sm">Active Devices</p>
                            <p className="text-2xl font-bold text-white">
                                {Object.values(controlStates).filter(Boolean).length} / {Object.keys(controlStates).length}
                            </p>
                        </div>
                    </div>
                </GlassCard>

                <GlassCard className="border-l-4 border-l-blue-500">
                    <div className="flex items-center gap-3">
                        <Zap className="text-blue-400" size={32} />
                        <div>
                            <p className="text-gray-400 text-sm">Power Consumption</p>
                            <p className="text-2xl font-bold text-white">
                                {(Object.values(controlStates).filter(Boolean).length * 12.5).toFixed(1)} kW
                            </p>
                        </div>
                    </div>
                </GlassCard>

                <GlassCard className="border-l-4 border-l-purple-500">
                    <div className="flex items-center gap-3">
                        <Wifi className="text-purple-400" size={32} />
                        <div>
                            <p className="text-gray-400 text-sm">Network Status</p>
                            <p className="text-2xl font-bold text-green-400">Connected</p>
                        </div>
                    </div>
                </GlassCard>
            </div>

            {/* 3D Animation Popup */}
            {activePopup && (
                <Control3DPopup
                    isOpen={!!activePopup}
                    onClose={() => setActivePopup(null)}
                    controlType={activePopup.device === 'lights_hw' || activePopup.device === 'lights_sw' ? 'lights' : activePopup.device}
                    controlName={activePopup.device.replace('_', ' ').toUpperCase()}
                    action={activePopup.action}
                />
            )}
        </div>
    );
};

export default Controls;
