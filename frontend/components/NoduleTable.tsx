// frontend/components/NoduleTable.tsx

'use client';

import { Nodule } from '@/types';
import RiskBadge from './RiskBadge';

interface NoduleTableProps {
    nodules: Nodule[];
    onNoduleClick?: (nodule: Nodule) => void;
}

export default function NoduleTable({ nodules, onNoduleClick }: NoduleTableProps) {
    if (nodules.length === 0) {
        return (
            <div className="p-8 text-center border border-neutral-200 rounded-xl bg-white">
                <p className="text-neutral-500">No nodules detected</p>
            </div>
        );
    }

    return (
        <div className="border border-neutral-200 rounded-xl bg-white overflow-hidden">
            <div className="overflow-x-auto">
                <table className="w-full">
                    <thead>
                        <tr className="border-b border-neutral-200 bg-neutral-50">
                            <th className="px-4 py-3 text-left text-xs font-semibold text-neutral-600 uppercase tracking-wider">
                                ID
                            </th>
                            <th className="px-4 py-3 text-left text-xs font-semibold text-neutral-600 uppercase tracking-wider">
                                Type
                            </th>
                            <th className="px-4 py-3 text-left text-xs font-semibold text-neutral-600 uppercase tracking-wider">
                                Location
                            </th>
                            <th className="px-4 py-3 text-left text-xs font-semibold text-neutral-600 uppercase tracking-wider">
                                Size (mm)
                            </th>
                            <th className="px-4 py-3 text-left text-xs font-semibold text-neutral-600 uppercase tracking-wider">
                                Volume (mm³)
                            </th>
                            <th className="px-4 py-3 text-left text-xs font-semibold text-neutral-600 uppercase tracking-wider">
                                Malignancy
                            </th>
                            <th className="px-4 py-3 text-left text-xs font-semibold text-neutral-600 uppercase tracking-wider">
                                Risk
                            </th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-neutral-200">
                        {nodules.map((nodule) => (
                            <tr
                                key={nodule.id}
                                onClick={() => onNoduleClick?.(nodule)}
                                className={`hover:bg-neutral-50 transition-colors ${onNoduleClick ? 'cursor-pointer' : ''
                                    }`}
                            >
                                <td className="px-4 py-4 text-sm font-medium text-neutral-900">
                                    #{nodule.id}
                                </td>
                                <td className="px-4 py-4 text-sm text-neutral-700 capitalize">
                                    {nodule.type.replace('-', ' ')}
                                </td>
                                <td className="px-4 py-4 text-sm text-neutral-700 capitalize">
                                    {nodule.location}
                                </td>
                                <td className="px-4 py-4 text-sm text-neutral-700">
                                    {nodule.long_axis_mm.toFixed(1)}
                                </td>
                                <td className="px-4 py-4 text-sm text-neutral-700">
                                    {nodule.volume_mm3.toFixed(1)}
                                </td>
                                <td className="px-4 py-4 text-sm text-neutral-700">
                                    {(nodule.prob_malignant * 100).toFixed(1)}%
                                </td>
                                <td className="px-4 py-4">
                                    <RiskBadge
                                        probability={nodule.prob_malignant}
                                        needsReview={nodule.uncertainty.needs_review}
                                    />
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
}