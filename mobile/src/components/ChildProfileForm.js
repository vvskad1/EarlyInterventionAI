/**
 * Child Profile Form Component
 */

import React from 'react';
import { View, StyleSheet } from 'react-native';
import { Card, Text, TextInput, Chip } from 'react-native-paper';
import { spacing } from '../config/theme';

const DOMAINS = [
    { value: 'communication', label: 'Communication' },
    { value: 'social', label: 'Social/Emotional' },
    { value: 'fine_motor', label: 'Fine Motor' },
    { value: 'gross_motor', label: 'Gross Motor' },
    { value: 'cognitive', label: 'Cognitive' },
    { value: 'adaptive', label: 'Adaptive' },
];

const ChildProfileForm = ({
    ageMonths,
    domains,
    notes,
    onAgeChange,
    onDomainsChange,
    onNotesChange,
}) => {
    const handleDomainToggle = (domain) => {
        const newDomains = domains.includes(domain)
            ? domains.filter(d => d !== domain)
            : [...domains, domain];
        onDomainsChange(newDomains);
    };

    const handleAgeChange = (text) => {
        if (text === '') {
            onAgeChange(null);
            return;
        }

        const age = parseInt(text, 10);
        if (!isNaN(age) && age >= 0 && age <= 36) {
            onAgeChange(age);
        }
    };

    return (
        <Card style={styles.card}>
            <Card.Content>
                <Text variant="titleMedium" style={styles.sectionTitle}>
                    Child Profile
                </Text>
                <Text variant="bodySmall" style={styles.subtitle}>
                    Provide a few details to generate a personalized support plan
                </Text>

                {/* Age Input */}
                <TextInput
                    mode="outlined"
                    label="Age (0-36 months)"
                    placeholder="Enter child's age in months"
                    value={ageMonths !== null ? ageMonths.toString() : ''}
                    onChangeText={handleAgeChange}
                    keyboardType="number-pad"
                    style={styles.ageInput}
                />

                {/* Areas of Concern */}
                <Text variant="labelLarge" style={styles.label}>
                    Areas of Concern
                </Text>
                <View style={styles.chipContainer}>
                    {DOMAINS.map((domain) => (
                        <Chip
                            key={domain.value}
                            selected={domains.includes(domain.value)}
                            onPress={() => handleDomainToggle(domain.value)}
                            style={styles.chip}
                        >
                            {domain.label}
                        </Chip>
                    ))}
                </View>

                {/* Notes */}
                <Text variant="labelLarge" style={styles.label}>
                    Observations/Notes
                </Text>
                <TextInput
                    mode="outlined"
                    placeholder="What have you observed during playtime, routines, or interactions?"
                    value={notes}
                    onChangeText={onNotesChange}
                    multiline
                    numberOfLines={4}
                    style={styles.notesInput}
                />
            </Card.Content>
        </Card>
    );
};

const styles = StyleSheet.create({
    card: {
        marginBottom: spacing.md,
    },
    sectionTitle: {
        fontWeight: '700',
        marginBottom: spacing.xs,
    },
    subtitle: {
        color: '#666',
        marginBottom: spacing.lg,
    },
    ageInput: {
        marginBottom: spacing.lg,
    },
    label: {
        marginBottom: spacing.sm,
        fontWeight: '600',
    },
    chipContainer: {
        flexDirection: 'row',
        flexWrap: 'wrap',
        marginBottom: spacing.lg,
    },
    chip: {
        marginRight: spacing.sm,
        marginBottom: spacing.sm,
    },
    notesInput: {
        minHeight: 100,
    },
});

export default ChildProfileForm;
