/**
 * Plan Display Component
 */

import React, { useState } from 'react';
import { View, StyleSheet } from 'react-native';
import { Card, Text, List, Divider } from 'react-native-paper';
import { spacing } from '../config/theme';

const PlanDisplay = ({ plan }) => {
    const [expandedGoals, setExpandedGoals] = useState(true);
    const [expandedStrategies, setExpandedStrategies] = useState(true);
    const [expandedAdvice, setExpandedAdvice] = useState(true);

    if (!plan) return null;

    return (
        <Card style={styles.card}>
            <Card.Content>
                <Text variant="titleLarge" style={styles.mainTitle}>
                    📋 Intervention Plan
                </Text>

                {/* Goals Section */}
                <List.Accordion
                    title="Goals"
                    expanded={expandedGoals}
                    onPress={() => setExpandedGoals(!expandedGoals)}
                    left={props => <List.Icon {...props} icon="target" />}
                >
                    <View style={styles.sectionContent}>
                        <Text variant="bodyMedium">{plan.Goals}</Text>
                    </View>
                </List.Accordion>

                <Divider />

                {/* Strategies Section */}
                <List.Accordion
                    title="Strategies"
                    expanded={expandedStrategies}
                    onPress={() => setExpandedStrategies(!expandedStrategies)}
                    left={props => <List.Icon {...props} icon="lightbulb-outline" />}
                >
                    <View style={styles.sectionContent}>
                        <Text variant="bodyMedium">{plan.Strategies}</Text>
                    </View>
                </List.Accordion>

                <Divider />

                {/* Advice for Parents Section */}
                <List.Accordion
                    title="Advice for Parents"
                    expanded={expandedAdvice}
                    onPress={() => setExpandedAdvice(!expandedAdvice)}
                    left={props => <List.Icon {...props} icon="account-heart" />}
                >
                    <View style={styles.sectionContent}>
                        <Text variant="bodyMedium">{plan['Advice for Parents']}</Text>
                    </View>
                </List.Accordion>
            </Card.Content>
        </Card>
    );
};

const styles = StyleSheet.create({
    card: {
        marginBottom: spacing.md,
    },
    mainTitle: {
        fontWeight: '700',
        marginBottom: spacing.md,
    },
    sectionContent: {
        padding: spacing.md,
        paddingTop: spacing.sm,
    },
});

export default PlanDisplay;
